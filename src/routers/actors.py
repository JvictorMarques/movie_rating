from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.actors import (
    ActorCreateResponseSchema,
    ActorCreateSchema,
    ActorDetailSchema,
    ActorListSchema,
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
    return await actors_service.update_actor(db, actor_id, actor)


@router.delete(
    path='/{actor_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete an actor/actress',
)
async def delete_user(db: Session, actor_id: int):
    await actors_service.delete_actor(db, actor_id)


@router.get(
    path='/{actor_id}',
    status_code=status.HTTP_200_OK,
    response_model=ActorDetailSchema,
    summary='Get an actor',
)
async def get_actor(db: Session, actor_id: int):
    return await actors_service.get_actor(db, actor_id)


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=ActorListSchema,
    summary='List all actors',
)
async def list_actors(
    db: Session,
    limit: Annotated[
        int, Query(gt=0, le=100, description='Number maximum of records')
    ] = 100,
    offset: Annotated[int, Query(ge=0, description='Page number')] = 0,
    search_filter: Annotated[
        Optional[str], Query(description='Search filter by name')
    ] = None,
):
    return await actors_service.list_actors(db, limit, offset, search_filter)
