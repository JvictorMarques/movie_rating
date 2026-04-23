from alembic.environment import Any
from sqlalchemy import Row, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Movie, MovieActor, UserMovie


async def check_movie_name_exists(
    db: AsyncSession, movie_name: str
) -> bool | None:
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


async def check_movie_exists(db: AsyncSession, movie_id: int) -> bool | None:
    return await db.scalar(select(exists().where(Movie.id == movie_id)))


async def check_user_rating_exists(
    db: AsyncSession, movie_id: int, user_id: int
) -> bool | None:
    return await db.scalar(
        select(
            exists().where(
                UserMovie.user_id == user_id, UserMovie.movie_id == movie_id
            )
        )
    )


async def create_user_rating(
    db: AsyncSession, movie_id: int, user_id: int, rating: float
) -> UserMovie:
    user_rating = UserMovie(movie_id=movie_id, user_id=user_id, rating=rating)
    db.add(user_rating)
    await db.commit()
    await db.refresh(user_rating)

    return user_rating


async def update_user_rating(
    db: AsyncSession, movie_id: int, user_id: int, rating: float
) -> UserMovie:
    user_rating = await db.scalar(
        select(UserMovie).where(
            UserMovie.user_id == user_id, UserMovie.movie_id == movie_id
        )
    )
    assert user_rating is not None
    user_rating.rating = rating
    await db.commit()
    await db.refresh(user_rating)

    return user_rating


async def get_movie_information(db: AsyncSession, movie_id: int) -> Row[Any]:
    avg_subquery = (
        select(func.avg(UserMovie.rating))
        .where(UserMovie.movie_id == movie_id)
        .scalar_subquery()
    )
    result = await db.execute(
        select(Movie, avg_subquery.label('avg_rating'))
        .where(Movie.id == movie_id)
        .options(selectinload(Movie.actors))
    )
    row = result.first()
    assert row is not None
    return row


async def delete_movie(db: AsyncSession, movie_id: int) -> None:
    movie = await db.get(Movie, movie_id)
    await db.delete(movie)
    await db.commit()


async def list_movies(
    db: AsyncSession,
    limit: int,
    offset: int,
    name_filter: str | None,
    rating_filter: float | None,
) -> list[Row[Any]]:
    avg_subquery = (
        select(func.avg(UserMovie.rating))
        .where(UserMovie.movie_id == Movie.id)
        .correlate(Movie)
        .scalar_subquery()
    )
    query = select(Movie, avg_subquery.label('avg_rating')).options(
        selectinload(Movie.actors)
    )
    if name_filter is not None:
        query = query.where(Movie.name.ilike(f'%{name_filter}%'))
    if rating_filter is not None:
        query = (
            query
            .join(Movie.user_movies)
            .group_by(Movie.id)
            .having(func.avg(UserMovie.rating) >= rating_filter)
        )
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.all())
