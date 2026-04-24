from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserMovie
from src.repositories import actors as actors_repository
from src.repositories import movies as movies_repository
from src.repositories import users as users_repository
from src.schemas.movies import (
    MovieCreateResponseSchema,
    MovieCreateSchema,
    MovieDetailSchema,
    MovieListSchema,
    MovieUpdateResponseSchema,
    MovieUpdateSchema,
)
from src.services.actors import ACTOR_NOT_FOUND
from src.services.users import USER_NOT_FOUND

MOVIE_EXISTS = 'Movie already exists'
MOVIE_NOT_FOUND = 'Movie not found'
MOVIE_HAS_RATE = 'Movie already has been rated'


async def create_movie(
    db: AsyncSession, movie: MovieCreateSchema
) -> MovieCreateResponseSchema:
    movie_exists = await movies_repository.check_movie_name_exists(
        db, movie.name
    )
    if movie_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=MOVIE_EXISTS
        )

    movie_data = movie.model_dump(exclude={'cast_ids'})
    db_movie = await movies_repository.create_movie(db, movie_data)

    if movie.cast_ids:
        actors_exists = await actors_repository.check_actors_exist(
            db, movie.cast_ids
        )
        if actors_missing_ids := set(movie.cast_ids) - actors_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{ACTOR_NOT_FOUND}: {actors_missing_ids}',
            )
        await movies_repository.add_cast_members(
            db, db_movie.id, movie.cast_ids
        )
        actors = await actors_repository.get_actors_information(
            db, movie.cast_ids
        )
    else:
        await db.commit()
        actors = None

    return MovieCreateResponseSchema(**db_movie.__dict__, cast=actors)


async def create_user_movie_rating(
    db: AsyncSession, movie_id: int, user_id: int, rating: float
) -> UserMovie:
    user_exists = await users_repository.check_user_exists(db, user_id)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    movie_exists = await movies_repository.check_movie_exists(db, movie_id)
    if not movie_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=MOVIE_NOT_FOUND
        )
    user_has_rated = await movies_repository.check_user_rating_exists(
        db, movie_id, user_id
    )
    if user_has_rated:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=MOVIE_HAS_RATE,
        )
    return await movies_repository.create_user_rating(
        db, movie_id, user_id, rating
    )


async def update_user_movie_rating(
    db: AsyncSession, movie_id: int, user_id: int, rating: float
) -> UserMovie:
    user_exists = await users_repository.check_user_exists(db, user_id)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )
    movie_exists = await movies_repository.check_movie_exists(db, movie_id)
    if not movie_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=MOVIE_NOT_FOUND
        )
    return await movies_repository.update_user_rating(
        db, movie_id, user_id, rating
    )


async def update_movie(
    db: AsyncSession, movie_id: int, movie: MovieUpdateSchema
) -> MovieUpdateResponseSchema:
    db_movie = await movies_repository.get_movie(db, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=MOVIE_NOT_FOUND
        )

    movie_data = movie.model_dump(exclude_unset=True)
    cast_ids = movie_data.pop('cast_ids', None)
    if 'name' in movie_data and movie_data['name'] != db_movie.name:
        name_exists = await movies_repository.check_movie_name_exists(
            db, movie_data['name']
        )
        if name_exists:
            raise HTTPException(status_code=409, detail=MOVIE_EXISTS)
    movie_updated = await movies_repository.update_movie(
        db, db_movie, movie_data
    )
    if cast_ids is not None:
        if cast_ids:
            actors_exist = await actors_repository.check_actors_exist(
                db, cast_ids
            )
            if actors_missing_ids := set(cast_ids) - actors_exist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'{ACTOR_NOT_FOUND}: {actors_missing_ids}',
                )
        await movies_repository.update_cast(db, movie_id, cast_ids)
        casting_updated = (
            await actors_repository.get_actors_information(db, cast_ids)
            or None
        )
    else:
        current_cast_ids = await movies_repository.get_movie_cast_ids(
            db, movie_id
        )
        casting_updated = (
            await actors_repository.get_actors_information(
                db, current_cast_ids
            )
            or None
        )
    rating = await movies_repository.get_movie_rating(db, movie_id)
    return MovieUpdateResponseSchema(
        **movie_updated.__dict__, cast=casting_updated, rating=rating
    )


async def get_movie(db: AsyncSession, movie_id: int) -> MovieDetailSchema:
    movie_exists = await movies_repository.check_movie_exists(db, movie_id)
    if not movie_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=MOVIE_NOT_FOUND
        )
    movie, avg_rating = await movies_repository.get_movie_information(
        db, movie_id
    )
    return MovieDetailSchema(
        **movie.__dict__, cast=movie.actors, rating=avg_rating
    )


async def delete_movie(db: AsyncSession, movie_id: int) -> None:
    movie_exists = await movies_repository.check_movie_exists(db, movie_id)
    if not movie_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=MOVIE_NOT_FOUND
        )
    await movies_repository.delete_movie(db, movie_id)


async def list_movies(
    db: AsyncSession,
    limit: int,
    offset: int,
    name_filter: str | None,
    rating_filter: float | None,
) -> MovieListSchema:
    rows = await movies_repository.list_movies(
        db, limit, offset, name_filter, rating_filter
    )
    return MovieListSchema(
        movies=[
            MovieDetailSchema(**m.__dict__, cast=m.actors, rating=avg_rating)
            for m, avg_rating in rows
        ],
        limit=limit,
        offset=offset,
    )
