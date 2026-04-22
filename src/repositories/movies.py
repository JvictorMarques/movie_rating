from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

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
    user_rating: UserMovie = await db.scalar(
        select(UserMovie).where(
            UserMovie.user_id == user_id, UserMovie.movie_id == movie_id
        )
    )
    user_rating.rating = rating
    await db.commit()
    await db.refresh(user_rating)

    return user_rating


# async def get_movie_information(db: AsyncSession, movie_id: int) -> Movie:
#     return await db.scalar((
#         select(Movie)
#         .where(Movie.id == movie_id)

#     ))
