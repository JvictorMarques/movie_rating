from pydantic import BaseModel, EmailStr

from src.schemas.common import Password


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: Password
