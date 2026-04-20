from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

Age = Annotated[int, Field(gt=1, lt=150)]
Name = Annotated[str, Field(min_length=2)]


class UserSchema(BaseModel):
    name: Name
    email: EmailStr
    age: Age
    password: SecretStr


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Name
    email: EmailStr
    age: Age

    created_at: datetime
    updated_at: datetime


class UserUpdateSchema(BaseModel):
    name: Optional[Name] = None
    email: Optional[EmailStr] = None
    age: Optional[Age] = None
    password: Optional[SecretStr] = None


class UserListPublicSchema(BaseModel):
    users: list[UserPublicSchema]
    limit: int
    offset: int
