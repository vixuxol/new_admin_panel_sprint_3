from uuid import UUID
from pydantic import BaseModel, Field


class PersonElasticDocument(BaseModel):
    id: UUID
    name: str


class FilmWorkElasticDocument(BaseModel):
    id: UUID
    imdb_rating: float
    genres: str
    title: str
    description: str
    directors: list[PersonElasticDocument] = Field(default_factory=list)
    directors_names: str = ""
    actors: list[PersonElasticDocument] = Field(default_factory=list)
    actors_names: str = ""
    writers: list[PersonElasticDocument] = Field(default_factory=list)
    writers_names: str = ""