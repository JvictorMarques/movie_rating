from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.schemas.actors import ActorInformationSchema
from src.schemas.common import Name, Rating


class MovieCreateSchema(BaseModel):
    name: Name
    synopsis: str
    director: Name
    cast_ids: Optional[set[int]] = None
    release_date: date


class MovieCreateResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    name: Name
    synopsis: str
    director: Name
    release_date: date
    cast: Optional[list[ActorInformationSchema]] = None

    created_at: datetime
    updated_at: datetime


class MovieDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Name
    synopsis: str
    director: Name
    release_date: date
    rating: Rating
    cast: list[ActorInformationSchema]

    created_at: datetime
    updated_at: datetime


class MovieUpdateSchema(BaseModel):
    name: Optional[Name] = None
    synopsis: Optional[str] = None
    director: Optional[Name] = None
    cast_ids: Optional[list[int]] = None
    release_date: Optional[date] = None


class MovieListSchema(BaseModel):
    movies: list[MovieDetailSchema]
    limit: int
    offset: int
