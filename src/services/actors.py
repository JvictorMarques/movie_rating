from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Actor
from src.repositories import actors as actors_repository
from src.schemas.actors import ActorCreateSchema

ACTOR_EXISTS = 'Actor/Actress already exists'


async def create_actor(db: AsyncSession, actor: ActorCreateSchema) -> Actor:
    actor_exists = await actors_repository.check_actor_name_exists(
        db, actor.name
    )
    if actor_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ACTOR_EXISTS
        )
    actor_data = actor.model_dump()
    return await actors_repository.create_actor(db, actor_data)
