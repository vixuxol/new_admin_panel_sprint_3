import logging
from uuid import UUID
from typing_extensions import Self
from types import TracebackType
from typing import Type, Optional


from extractor.datatypes import AggregateFilmWorkRecord
from transformer.base_transformer import BaseTransformer
from loader.datatypes import FilmWorkElasticDocument, PersonElasticDocument

class DataTransformer(BaseTransformer):
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def process(self, records: list[AggregateFilmWorkRecord]) -> list[FilmWorkElasticDocument]:
        transformed_records = {}
        for record in records:
            es_document = self._get_film_work_es_document(record, transformed_records)
            enriched_es_document = self._enrich_by_persons_info(es_document, record)
            transformed_records[enriched_es_document.id] = enriched_es_document

        self._logger.info("Transformed %s records successfully.", len(records))
        return transformed_records.values()

    def _get_film_work_es_document(
            self, 
            record: AggregateFilmWorkRecord, 
            transformed_records: dict[UUID:FilmWorkElasticDocument]
        ) -> FilmWorkElasticDocument:
        if (model := transformed_records.get(record["film_work_id"])) is not None:
            return model
        return FilmWorkElasticDocument(
            id=record["film_work_id"],
            imdb_rating=record["film_work_rating"] or 0.0,
            title=record["film_work_title"],
            description=record["film_work_description"] or "",
            genres=record["genre_name"] or "",
        )

    def _enrich_by_persons_info(self, es_document: FilmWorkElasticDocument, record: AggregateFilmWorkRecord) -> FilmWorkElasticDocument:
        role = {
            "DR": "director",
            "WR": "writer",
            "AC": "actor",
            "PR": "producer"
        }.get(record["person_film_work_role"], "")
        if role:
            person = PersonElasticDocument(id=record["person_id"], name=record["person_full_name"])
            persons_by_specified_role = getattr(es_document, f"{role}s")
            if persons_by_specified_role is not None and person not in persons_by_specified_role:
                persons_by_specified_role.append(person)
                setattr(es_document, f"{role}s", persons_by_specified_role)
                setattr(es_document, f"{role}s_names", ", ".join([person.name for person in persons_by_specified_role]))
        return es_document
