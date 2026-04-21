from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Movie, MovieActor


async def check_movie_exists(db: AsyncSession, movie_name: str) -> bool | None:
    return await db.scalar(select(exists().where(Movie.name == movie_name)))


async def create_movie(db: AsyncSession, movie: dict) -> Movie:
    db_movie = Movie(**movie)

    db.add(db_movie)
    await db.flush()
    await db.refresh(db_movie)

    return db_movie


async def add_cast_members(
    db: AsyncSession, movie_id: int, movie_cast_members_ids: set[int]
) -> None:
    for actor_id in movie_cast_members_ids:
        db.add(MovieActor(movie_id=movie_id, actor_id=actor_id))
    await db.commit()
