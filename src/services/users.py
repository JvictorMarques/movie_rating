from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import EMAIL_EXISTS, USER_NOT_FOUND
from src.core.security import get_password_hash
from src.models.users import User
from src.repositories import users as users_repo
from src.schemas.users import (
    UserCreateSchema,
    UserListSchema,
    UserUpdateSchema,
)


async def create_user(db: AsyncSession, user_data: UserCreateSchema) -> User:
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
) -> UserListSchema:
    users = await users_repo.list_all_users(db, limit, offset, search_filter)
    return UserListSchema(users=users, limit=limit, offset=offset)


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
