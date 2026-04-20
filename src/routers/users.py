from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.users import (
    UserListPublicSchema,
    UserPublicSchema,
    UserSchema,
    UserUpdateSchema,
)
from src.services import users as users_service

router = APIRouter()
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=UserListPublicSchema,
    summary='List all users',
)
async def list_users(
    db: Session,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description='Number maximum of records'),
    ] = 100,
    offset: Annotated[int, Query(ge=0, description='Page number')] = 0,
    search_filter: Annotated[
        Optional[str], Query(description='Search filter by name')
    ] = None,
):
    return await users_service.list_users(db, limit, offset, search_filter)


@router.get(
    path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary='Get an users',
)
async def get_user(db: Session, user_id: int):
    return await users_service.get_user(db, user_id)


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Create an user',
)
async def create_user(db: Session, user: UserSchema):
    return await users_service.create_user(db, user)


@router.delete(
    path='/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete an user',
)
async def delete_user(db: Session, user_id: int):
    await users_service.delete_user(db, user_id)


@router.put(
    path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary='Update an user',
)
async def update_user(
    db: Session, user_id: int, update_data: UserUpdateSchema
):
    return await users_service.update_user(db, user_id, update_data)
