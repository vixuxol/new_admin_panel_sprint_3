from abc import ABC, abstractmethod

from extractor.datatypes import AggregateFilmWorkRecord
from loader.datatypes import FilmWorkElasticDocument


class BaseTransformer(ABC):

    @abstractmethod
    def process(self, records_from_db: list[AggregateFilmWorkRecord]) -> None:
        """Prepare records to ElasticSearch"""
        raise NotImplementedError
