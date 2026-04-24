from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.actors import (
    ActorCreateResponseSchema,
    ActorCreateSchema,
    ActorDetailSchema,
    ActorUpdateSchema,
)
from src.services import actors as actors_service

router = APIRouter()
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=ActorCreateResponseSchema,
    summary='Create an actor/actress',
)
async def create_actor(db: Session, actor: ActorCreateSchema):
    return await actors_service.create_actor(db, actor)


@router.put(
    path='/{actor_id}',
    status_code=status.HTTP_200_OK,
    response_model=ActorDetailSchema,
    summary='Update an actor/actress',
)
async def update_user(db: Session, actor_id: int, actor: ActorUpdateSchema):
    pass


# TODO - Update actors
# TODO - Get actors
# TODO - List actors
# TODO - Delete actors
