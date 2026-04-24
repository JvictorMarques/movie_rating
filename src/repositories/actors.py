from collections.abc import Sequence

from sqlalchemy import Row, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Actor


async def get_actor(db: AsyncSession, actor_id: int) -> Actor | None:
    return await db.get(Actor, actor_id)


async def check_actor_exist(db: AsyncSession, actor_id: int) -> bool | None:
    return await db.scalar(select(exists().where(Actor.id == actor_id)))


async def check_actors_exist(
    db: AsyncSession, actor_ids: list[int]
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
    db: AsyncSession, actors_id: list[int]
) -> Sequence[Row]:
    result = await db.execute(
        select(Actor.id, Actor.name, Actor.age).where(Actor.id.in_(actors_id))
    )
    return result.all()


async def update_actor(
    db: AsyncSession, update_actor_data: dict, db_actor: Actor
) -> Actor:
    for key, value in update_actor_data.items():
        setattr(db_actor, key, value)
    await db.commit()
    await db.refresh(db_actor)

    return db_actor


async def delete_actor(db: AsyncSession, actor: Actor) -> None:
    await db.delete(actor)
    await db.commit()
