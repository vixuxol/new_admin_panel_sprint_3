import datetime as dt
import json
from pydantic_settings import BaseSettings
from typing import Any

class ETL_Settings(BaseSettings):
    debug: bool = True
    log_level: str = "DEBUG" if debug else "INFO"
    refresh_interval: dt.timedelta = dt.timedelta(seconds=20)

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    redis_host: str
    redis_port: str
    redis_db: str

    elastic_host: str
    elastic_port: str
    elastic_index: str = "movies"
    elastic_index_mapping_file_path: str


    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgres://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def logging_config(self) -> dict[str, Any]:
        return {
                "version": 1,
                "root": {
                    "handlers": ["console"],
                    "level": self.log_level,
                },
                "handlers": {"console": {"formatter": "std_out", "class": "logging.StreamHandler", "level": "DEBUG"}},
                "formatters": {
                    "std_out": {
                        "format": "%(asctime)s | %(levelname)s | %(module)s.%(funcName)s.%(lineno)d - %(message)s",
                        "datefmt": "%d-%m-%Y %I:%M:%S",
                    }
                },
            }
    
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def elastic_dsn(self) -> str:
        return f"http://{self.elastic_host}:{self.elastic_port}"
    
    @property
    def elastic_mapping(self) -> dict:
        with open(self.elastic_index_mapping_file_path, "r+", encoding="utf-8") as mapping_file:
            mapping = json.load(mapping_file)
        return mapping