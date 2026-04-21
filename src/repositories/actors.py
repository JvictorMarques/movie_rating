from collections.abc import Sequence

from sqlalchemy import Row, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Actor


async def check_actor_exists(
    db: AsyncSession, actor_ids: set[int]
) -> set[int]:
    result = await db.scalars(select(Actor.id).where(Actor.id.in_(actor_ids)))
    return set(result.all())


async def check_actor_name_exists(
    db: AsyncSession, actor_name: str
) -> bool | None:
    return await db.scalar(select(exists().where(Actor.name == actor_name)))


async def create_actor(db: AsyncSession, actor: dict) -> Actor:
    db_actor = Actor(**actor)

    db.add(db_actor)
    await db.commit()
    await db.refresh(db_actor)

    return db_actor


async def get_actors_information(
    db: AsyncSession, actors_id: set[int]
) -> Sequence[Row]:
    result = await db.execute(
        select(Actor.id, Actor.name, Actor.age).where(Actor.id.in_(actors_id))
    )
    return result.all()
