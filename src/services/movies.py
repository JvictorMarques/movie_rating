from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import actors as actors_repository
from src.repositories import movies as movies_repository
from src.schemas.movies import MovieCreateResponseSchema, MovieCreateSchema

MOVIE_EXISTS = 'Movie already exists'


async def create_movie(
    db: AsyncSession, movie: MovieCreateSchema
) -> MovieCreateResponseSchema:
    movie_exists = await movies_repository.check_movie_exists(db, movie.name)
    if movie_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=MOVIE_EXISTS
        )

    movie_data = movie.model_dump(exclude={'cast_ids'})
    db_movie = await movies_repository.create_movie(db, movie_data)

    if movie.cast_ids:
        actors_exists = await actors_repository.check_actor_exists(
            db, movie.cast_ids
        )
        if actors_missing_ids := movie.cast_ids - actors_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Actor not found: {actors_missing_ids}',
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
