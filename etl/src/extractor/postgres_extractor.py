import datetime as dt
import logging
from types import TracebackType
from typing import AsyncGenerator, Type, Optional

import asyncpg
from typing_extensions import Self

from extractor.datatypes import AggregateFilmWorkRecord, PersonRecord, FilmWorkRecord
from extractor.base_extractor import BaseExtractor


class PostgresExtractor(BaseExtractor):
    BATCH_SIZE = 100

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._connection = None
        self._logger = logging.getLogger(__name__)

    async def __aenter__(self) -> Self:
        self._logger.debug("Trying to connect to postgres with dsn: %s", self._dsn)
        self._connection: asyncpg.connection.Connection = await asyncpg.connect(self._dsn)
        self._logger.debug("Connected to PostgreSQL successfully.")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._logger.debug("Closing connection to PostgreSQL")
        await self._connection.close()
        self._logger.info("Connection to PostgreSQL closed.")

    async def extract_records_from_db(self, last_extraction_datetime: dt.datetime) -> AsyncGenerator[AggregateFilmWorkRecord, None]:
        modified_persons_ids = await self._extract_modified_persons_ids(last_extraction_datetime)
        modified_film_works_ids = await self._extract_film_work_ids(modified_persons_ids, last_extraction_datetime)
        async for records in self._extract_records_by_related_film_works_ids(modified_film_works_ids):
            self._logger.debug("Fetched %s records.", len(records))
            yield records

    async def _extract_modified_persons_ids(self, last_extraction_datetime: dt.datetime) -> list[PersonRecord]:
        self._logger.debug("Trying to extract modified person's ids for a given period of time")
        sql_query = f"SELECT id FROM content.person WHERE updated_at > '{last_extraction_datetime}';"
        person_ids = await self._connection.fetch(sql_query)
        self._logger.debug("Found %s modified persons since '%s'.", len(person_ids), last_extraction_datetime)
        return person_ids

    async def _extract_film_work_ids(
        self, 
        persons_ids: list[PersonRecord], 
        last_extraction_datetime: dt.datetime
    ) -> list[FilmWorkRecord]:
        where_conditions = [f"fw.updated_at > '{last_extraction_datetime}'"]
        if persons_ids:
            persons = ", ".join([f"'{record['id']}'" for record in persons_ids])
            where_conditions.append(f"pfw.person_id IN ({persons})")
        sql_query = f"""
            SELECT fw.id
            FROM content.film_work AS fw
            LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
            WHERE {" OR ".join(where_conditions)};
        """
        film_work_ids = await self._connection.fetch(sql_query)
        self._logger.debug("Found %s modified film works", len(film_work_ids))
        return film_work_ids

    async def _extract_records_by_related_film_works_ids(
        self,
        film_works_ids: list[FilmWorkRecord]
    ) -> AsyncGenerator[AggregateFilmWorkRecord, None]:
        film_works = ", ".join([f"'{record['id']}'" for record in film_works_ids])
        sql_query = f"""
            SELECT
                fw.id AS film_work_id,
                fw.title AS film_work_title,
                fw.description AS film_work_description,
                fw.rating AS film_work_rating,
                fw.type AS film_work_type,
                pfw.role AS person_film_work_role,
                p.id AS person_id,
                p.full_name AS person_full_name,
                g.name AS genre_name
            FROM content.film_work AS fw
                LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
                LEFT JOIN content.person AS p ON p.id = pfw.person_id
                LEFT JOIN content.genre_film_work AS gfw ON gfw.film_work_id = fw.id
                LEFT JOIN content.genre AS g ON g.id = gfw.genre_id
            WHERE fw.id IN ({film_works});
        """
        async with self._connection.transaction():
            result = await self._connection.cursor(sql_query)
            while records := await result.fetch(self.BATCH_SIZE):
                yield records
