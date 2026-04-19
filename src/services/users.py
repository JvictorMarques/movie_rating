from typing import Optional

from fastapi import HTTPException, status
from pwdlib import PasswordHash
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.repositories import users as users_repo
from src.schemas.users import (
    UserListPublicSchema,
    UserSchema,
)


def get_password_hash(password: str) -> str:
    return PasswordHash.recommended().hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PasswordHash.recommended().verify(plain_password, hashed_password)


async def create_user(db: AsyncSession, user_data: UserSchema) -> User:
    email_exists = await users_repo.email_exists(db, user_data.email)
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email already exists',
        )
    user_data.password = SecretStr(
        get_password_hash(user_data.password.get_secret_value())
    )
    return await users_repo.create_user(db, user_data)


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await users_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    await users_repo.delete_user(db, user_id)


async def list_users(
    db: AsyncSession, limit: int, offset: int, search_filter: Optional[str]
) -> UserListPublicSchema:
    users = await users_repo.list_all_users(db, limit, offset, search_filter)
    return UserListPublicSchema(users=users, limit=limit, offset=offset)


async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await users_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    return user


# async def update_user(db: AsyncSession, user_id: int) -> User: #TODO
#     pass
