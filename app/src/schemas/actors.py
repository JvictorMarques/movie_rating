from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.schemas.common import Age, Name


class ActorCreateSchema(BaseModel):
    name: Name
    age: Age


class ActorCreateResponseSchema(BaseModel):
    id: int
    name: Name
    age: Age

    created_at: datetime
    updated_at: datetime


class ActorInformationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Name
    age: Age


class ActorDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Name
    age: Age

    created_at: datetime
    updated_at: datetime


class ActorUpdateSchema(BaseModel):
    name: Optional[Name] = None
    age: Optional[Age] = None


class ActorListSchema(BaseModel):
    actors: list[ActorDetailSchema]
    limit: int
    offset: int
