import logging
from typing_extensions import Optional, Self, Type
from types import TracebackType
from uuid import UUID


from extractor.datatypes import AggregateFilmWorkRecord
from transformer.base_transformer import BaseTransformer
from loader.datatypes import FilmWorkElasticDocument, PersonElasticDocument

class DataTransformer(BaseTransformer):
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def __enter__(self) -> Self:
        self.transformed_records = {}
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.transformed_records = {}

    def process(self, records: list[AggregateFilmWorkRecord]) -> None:
        for record in records:
            es_document = self._get_film_work_es_document(record)
            enriched_es_document = self._enrich_by_genre_info(self._enrich_by_persons_info(es_document, record), record)
            self.transformed_records[enriched_es_document.id] = enriched_es_document

        self._logger.info("Transformed %s records successfully.", len(records))

    def _get_film_work_es_document(
            self, 
            record: AggregateFilmWorkRecord, 
        ) -> FilmWorkElasticDocument:
        if (model := self.transformed_records.get(record["film_work_id"])) is not None:
            return model
        return FilmWorkElasticDocument(
            id=record["film_work_id"],
            imdb_rating=record["film_work_rating"],
            title=record["film_work_title"] or "",
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
            if person not in persons_by_specified_role:
                persons_by_specified_role.append(person)
                setattr(es_document, f"{role}s", persons_by_specified_role)
                setattr(es_document, f"{role}s_names", " ".join([person.name for person in persons_by_specified_role]))
        return es_document
    
    def _enrich_by_genre_info(self, es_document: FilmWorkElasticDocument, record: AggregateFilmWorkRecord) -> FilmWorkElasticDocument:
        current_genres = es_document.genres.split(" ")
        genre = record["genre_name"]
        if genre and genre not in current_genres:
            current_genres.append(genre)
            es_document.genres = " ".join(current_genres)
        return es_document
