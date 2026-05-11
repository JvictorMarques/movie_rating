import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import ACTOR_EXISTS, ACTOR_NOT_FOUND
from src.models import Actor
from src.repositories import actors as actors_repository
from src.schemas.actors import (
    ActorCreateSchema,
    ActorListSchema,
    ActorUpdateSchema,
)

logger = logging.getLogger(__name__)


async def create_actor(db: AsyncSession, actor: ActorCreateSchema) -> Actor:
    actor_exists = await actors_repository.check_actor_name_exists(
        db, actor.name
    )
    if actor_exists:
        logger.warning(ACTOR_EXISTS, extra={'actor_name': actor.name})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ACTOR_EXISTS
        )
    actor_data = actor.model_dump()
    db_actor = await actors_repository.create_actor(db, actor_data)
    logger.info(
        'Actor created',
        extra={'actor_id': db_actor.id, 'actor_name': db_actor.name},
    )
    return db_actor


async def update_actor(
    db: AsyncSession, actor_id: int, actor: ActorUpdateSchema
) -> Actor:
    db_actor = await actors_repository.get_actor(db, actor_id)
    if not db_actor:
        logger.debug(ACTOR_NOT_FOUND, extra={'actor_id': actor_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ACTOR_NOT_FOUND
        )
    actor_name_exists = (
        actor.name
        and await actors_repository.check_actor_name_exists(db, actor.name)
    )
    if actor_name_exists:
        logger.warning(ACTOR_EXISTS, extra={'actor_name': actor.name})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ACTOR_EXISTS
        )
    actor_data = actor.model_dump(exclude_unset=True)
    logger.debug(
        'Updating actor',
        extra={'actor_id': actor_id, 'fields': list(actor_data.keys())},
    )
    db_actor = await actors_repository.update_actor(db, actor_data, db_actor)
    logger.info('Actor updated', extra={'actor_id': actor_id})
    return db_actor


async def delete_actor(db: AsyncSession, actor_id: int) -> None:
    db_actor = await actors_repository.get_actor(db, actor_id)
    if not db_actor:
        logger.debug(ACTOR_NOT_FOUND, extra={'actor_id': actor_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ACTOR_NOT_FOUND
        )
    await actors_repository.delete_actor(db, db_actor)
    logger.info('Actor deleted', extra={'actor_id': actor_id})


async def get_actor(db: AsyncSession, actor_id: int) -> Actor:
    db_actor = await actors_repository.get_actor(db, actor_id)
    if not db_actor:
        logger.debug(ACTOR_NOT_FOUND, extra={'actor_id': actor_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ACTOR_NOT_FOUND
        )
    return db_actor


async def list_actors(
    db: AsyncSession, limit: int, offset: int, search_filter: str | None
) -> ActorListSchema:
    logger.debug(
        'Listing actors',
        extra={
            'limit': limit,
            'offset': offset,
            'search_filter': search_filter,
        },
    )
    actors = await actors_repository.list_actors(
        db, limit, offset, search_filter
    )
    return ActorListSchema(actors=actors, limit=limit, offset=offset)
