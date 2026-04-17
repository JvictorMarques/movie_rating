from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

Age = Annotated[int, Field(gt=1, lt=150)]


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    age: Age
    password: SecretStr


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    age: Age


class UserUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[Age] = None
    password: Optional[SecretStr] = None


class UserListPublicSchema(BaseModel):
    users: list[UserPublicSchema]
