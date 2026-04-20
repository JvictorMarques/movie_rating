from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.schemas.common import Age, Name, Rating


class ActorSchema(BaseModel):
    name: Name
    age: Age


class ActorPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Name
    age: Age
    rating: Rating


class ActorUpdateSchema(BaseModel):
    name: Optional[Name] = None
    age: Optional[Age] = None


class ActorListSchema(BaseModel):
    actors: list[ActorPublicSchema]
    limit: int
    offset: int
