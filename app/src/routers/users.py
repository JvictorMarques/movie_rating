from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models.users import User
from src.schemas.users import (
    UserCreateSchema,
    UserDetailSchema,
    UserListSchema,
    UserUpdateSchema,
)
from src.services import auth as auth_services
from src.services import users as users_service

router = APIRouter()
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(auth_services.get_current_user)]


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=UserListSchema,
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
    response_model=UserDetailSchema,
    summary='Get an user',
)
async def get_user(db: Session, user_id: int):
    return await users_service.get_user(db, user_id)


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserDetailSchema,
    summary='Create an user',
)
async def create_user(db: Session, user: UserCreateSchema):
    return await users_service.create_user(db, user)


@router.put(
    path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserDetailSchema,
    summary='Update an user',
)
async def update_user(
    db: Session,
    current_user: CurrentUser,
    user_id: int,
    update_data: UserUpdateSchema,
):
    auth_services.verify_user_ownership(current_user, user_id)
    return await users_service.update_user(db, user_id, update_data)


@router.delete(
    path='/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete an user',
)
async def delete_user(db: Session, current_user: CurrentUser, user_id: int):
    auth_services.verify_user_ownership(current_user, user_id)
    await users_service.delete_user(db, user_id)
