import datetime as dt

from common.state_storage.base_storage import BaseStorage
from common.decorators import backoff
from extractor.base_extractor import BaseExtractor
from loader.base_loader import BaseLoader
from transformer.base_transformer import BaseTransformer


@backoff()
async def etl_process(
        extractor: BaseExtractor,
        transformer: BaseTransformer,
        loader: BaseLoader,
        state_storage: BaseStorage
    ):
    state: dict = await state_storage.retrieve_state()
    last_extraction_datetime = state.get("last_etl_processing", dt.datetime.min)

    documents = []
    async for records in extractor.extract_records_from_db(last_extraction_datetime):
        documents.extend(transformer.process(records))

    await loader.update_index(documents)
    await state_storage.save_state({"last_etl_processing": dt.datetime.now().timestamp()})