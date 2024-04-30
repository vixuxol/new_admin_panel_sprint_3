from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class PersonElasticDocument(BaseModel):
    id: UUID
    name: str


class FilmWorkElasticDocument(BaseModel):
    id: UUID
    imdb_rating: Optional[float] = None
    genres: list[str] = Field(default_factory=list)
    title: str = ""
    description: str = ""
    directors: list[PersonElasticDocument] = Field(default_factory=list)
    directors_names: list[str] = Field(default_factory=list)
    actors: list[PersonElasticDocument] = Field(default_factory=list)
    actors_names: list[str] = Field(default_factory=list)
    writers: list[PersonElasticDocument] = Field(default_factory=list)
    writers_names: list[str] = Field(default_factory=list)