import asyncio
import logging
import logging.config

from common.settings import ETL_Settings
from common.state_storage.redis_storage import RedisStorage
from extractor.postgres_extractor import PostgresExtractor
from loader.loader import Loader
from transformer.data_transformer import DataTransformer
from etl_process import etl_process

async def main() -> None:
    settings = ETL_Settings()
    logging.config.dictConfig(settings.logging_config)
    logger = logging.getLogger(__name__)

    async with (
        PostgresExtractor(settings.postgres_dsn) as extractor,
        Loader(settings.elastic_dsn, settings.elastic_index, settings.elastic_mapping) as loader,
        RedisStorage(settings.redis_url) as state_storage
    ):
        while True:
            try:
                with DataTransformer() as data_transformer:
                    await etl_process(extractor, data_transformer, loader, state_storage)
            except Exception as error:
                logger.exception(error)
                refresh_interval = settings.refresh_interval.total_seconds() * 10
                logger.debug("Trying after %s.", refresh_interval)
            else:
                refresh_interval = settings.refresh_interval.total_seconds()
                logger.debug("ETL pipeline work finished sucessfully.")
            finally:
                await asyncio.sleep(refresh_interval)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())