from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.users import (
    UserListPublicSchema,
    UserPublicSchema,
    UserSchema,
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
async def list_users(db: Session):
    return await users_service.list_users(db)


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
