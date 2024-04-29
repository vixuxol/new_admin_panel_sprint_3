import asyncio
import logging
from asyncio import Semaphore
from types import TracebackType
from typing import Sequence, Optional, Type

from elasticsearch import AsyncElasticsearch
from typing_extensions import Self, Final

from loader.base_loader import BaseLoader
from loader.datatypes import FilmWorkElasticDocument


class Loader(BaseLoader):
    SEMAPHORE_LIMIT: Final[int] = 20

    def __init__(self, dsn: str, index: str, mapping: dict) -> None:
        self._dsn = dsn
        self._index = index
        self._mapping = mapping
        self._es = None
        self._logger = logging.getLogger(__name__)

    async def __aenter__(self) -> Self:
        self._logger.debug("Trying to connect to ES with: %s", self._dsn)
        self._es = AsyncElasticsearch(self._dsn)
        await self._es.ping()
        self._logger.info("Connected to ElasticSearch successfully.")
        await self._create_index_if_not_exists()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._logger.debug("Closing connection to ElasticSearch")
        await self._es.close()
        self._es = None
        self._logger.info("Connection to ElasticSearch closed.")

    async def update_index(self, documents: list[FilmWorkElasticDocument]) -> None:
        semaphore = asyncio.Semaphore(self.SEMAPHORE_LIMIT)
        document_updating_coroutines = [self._update_document(document, semaphore) for document in documents]
        self._logger.info("Loading %s documents to ElasticSearch...", len(documents))
        await asyncio.gather(*document_updating_coroutines)
        self._logger.info("Loaded %s documents to ElasticSearch successfully.", len(documents))

    async def _update_document(self, document: FilmWorkElasticDocument, semaphore: Semaphore) -> None:
        async with semaphore:
            await self._es.index(index=self._index, id=document.id, body=document.model_dump())

    async def _create_index_if_not_exists(self) -> None:
        self._logger.debug("Check index with name: %s existing in ES", self._index)
        exists = await self._es.indices.exists(index=self._index)
        if not exists:
            self._logger.info("Not found index with name: %s in ElasticSearch. Creating...", self._index)
            await self._es.indices.create(index=self._index, body=self._mapping)
            self._logger.info("Index with name: %s created successfully.", self._index)
        else:
            self._logger.info("Index with name: %s already exists in ElasticSearch.", self._index)
