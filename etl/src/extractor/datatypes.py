import asyncpg
from uuid import UUID

class FilmWorkRecord(asyncpg.Record):
    id: UUID

class PersonRecord(asyncpg.Record):
    id: UUID

class AggregateFilmWorkRecord(asyncpg.Record):
    film_work_id: UUID
    film_work_title: str
    film_work_description: str
    film_work_rating: float
    film_work_type: str
    person_film_work_role: str
    person_id: UUID
    person_full_name: str
    genre_name: str