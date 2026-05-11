from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from src.schemas.common import Age, Name, Password


class UserCreateSchema(BaseModel):
    name: Name
    email: EmailStr
    age: Age
    password: Password


class UserDetailSchema(BaseModel):
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
    password: Optional[Password] = None


class UserListSchema(BaseModel):
    users: list[UserDetailSchema]
    limit: int
    offset: int
