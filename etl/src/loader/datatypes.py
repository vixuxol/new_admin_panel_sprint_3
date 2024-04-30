from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class PersonElasticDocument(BaseModel):
    id: UUID
    name: str


class FilmWorkElasticDocument(BaseModel):
    id: UUID
    imdb_rating: Optional[float] = None
    genres: str = ""
    title: str = ""
    description: str = ""
    directors: list[PersonElasticDocument] = Field(default_factory=list)
    directors_names: str = ""
    actors: list[PersonElasticDocument] = Field(default_factory=list)
    actors_names: str = ""
    writers: list[PersonElasticDocument] = Field(default_factory=list)
    writers_names: str = ""