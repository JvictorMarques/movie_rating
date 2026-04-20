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
    UserUpdateSchema,
)

USER_NOT_FOUND = 'User not found'
EMAIL_EXISTS = 'Email already exists'


def get_password_hash(password: SecretStr) -> SecretStr:
    return SecretStr(
        PasswordHash.recommended().hash(password.get_secret_value())
    )


def verify_password(
    plain_password: SecretStr, hashed_password: SecretStr
) -> bool:
    return PasswordHash.recommended().verify(
        plain_password.get_secret_value(),
        hashed_password.get_secret_value(),
    )


async def create_user(db: AsyncSession, user_data: UserSchema) -> User:
    email_exists = await users_repo.email_exists(db, user_data.email)
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EMAIL_EXISTS,
        )
    user_data.password = get_password_hash(user_data.password)
    return await users_repo.create_user(db, user_data)


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await users_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
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
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    return user


async def update_user(
    db: AsyncSession, user_id: int, update_data: UserUpdateSchema
) -> User:
    user = await users_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    data = update_data.model_dump(exclude_unset=True)

    if 'email' in data and data['email'] != user.email:
        email_exists = await users_repo.email_exists(db, data['email'])
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=EMAIL_EXISTS
            )
    if 'password' in data:
        data['password'] = get_password_hash(data['password'])
    return await users_repo.update_user(db, user, data)
