from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.schemas.actors import ActorInformationSchema
from src.schemas.common import Name, Rating


class MovieCreateSchema(BaseModel):
    name: Name
    synopsis: str
    director: Name
    cast_ids: Optional[list[int]] = None
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


class MovieRatingSchema(BaseModel):
    rating: Rating


class MovieCreateRatingResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    movie_id: int
    rating: Rating

    created_at: datetime
    updated_at: datetime


class MovieRatingUpdateResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    movie_id: int
    rating: Rating

    updated_at: datetime


class MovieDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Name
    synopsis: str
    director: Name
    release_date: date
    rating: Optional[Rating] = None
    cast: Optional[list[ActorInformationSchema]] = None

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
