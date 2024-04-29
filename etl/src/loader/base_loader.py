from abc import ABC, abstractmethod

from loader.datatypes import FilmWorkElasticDocument


class BaseLoader(ABC):

    @abstractmethod
    def update_index(self, documents: list[FilmWorkElasticDocument]) -> None:
        raise NotImplementedError