from abc import ABC, abstractmethod
import datetime as dt


class BaseExtractor(ABC):
    @abstractmethod
    async def extract_records_from_db(self, last_extraction_datetime: dt.datetime):
        raise NotImplementedError