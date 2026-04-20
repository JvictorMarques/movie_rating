from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.schemas.common import Name, Rating


class MovieSchema(BaseModel):
    name: Name
    synopsis: str
    director: Name
    release_date: date


class MoviePublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Name
    synopsis: str
    director: Name
    release_date: date
    rating: Rating

    created_at: datetime
    updated_at: datetime


class MovieUpdateSchema(BaseModel):
    name: Optional[Name] = None
    synopsis: Optional[str] = None
    director: Optional[Name] = None
    release_date: Optional[date] = None


class MovieListSchema(BaseModel):
    movies: list[MoviePublicSchema]
    limit: int
    offset: int
