import datetime as dt

from common.state_storage.base_storage import BaseStorage
from common.decorators import backoff
from extractor.base_extractor import BaseExtractor
from loader.base_loader import BaseLoader
from transformer.base_transformer import BaseTransformer


@backoff(1, 2, 60)
async def etl_process(
        extractor: BaseExtractor,
        transformer: BaseTransformer,
        loader: BaseLoader,
        state_storage: BaseStorage
    ):
    state: dict = await state_storage.retrieve_state()
    try:
        last_extraction_datetime = dt.datetime.utcfromtimestamp(float(state.pop("last_etl_processing")))
    except KeyError:
        last_extraction_datetime = dt.datetime.min

    async for records in extractor.extract_records_from_db(last_extraction_datetime):
        transformer.process(records)
    
    await loader.update_index(transformer.transformed_records.values())
    await state_storage.save_state({"last_etl_processing": dt.datetime.now().timestamp()})