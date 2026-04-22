from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.movies import (
    MovieCreateRatingResponseSchema,
    MovieCreateResponseSchema,
    MovieCreateSchema,
    MovieRatingSchema,
    MovieRatingUpdateResponseSchema,
)
from src.services import movies as movie_services

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=MovieCreateResponseSchema,
    summary='Create a movie',
)
async def create_movie(db: Session, movie: MovieCreateSchema):
    return await movie_services.create_movie(db, movie)


@router.post(
    path='/{movie_id}/ratings',
    status_code=status.HTTP_201_CREATED,
    response_model=MovieCreateRatingResponseSchema,
    summary='Rate a movie',
)
async def create_user_movie_rating(
    db: Session, movie_id: int, current_user_id: int, movie: MovieRatingSchema
):
    return await movie_services.create_user_movie_rating(
        db, movie_id, current_user_id, movie.rating
    )


@router.put(
    path='/{movie_id}/ratings',
    status_code=status.HTTP_200_OK,
    response_model=MovieRatingUpdateResponseSchema,
    summary='Update a movie rating',
)
async def update_user_movie_rating(
    db: Session, movie_id: int, current_user_id: int, movie: MovieRatingSchema
):
    return await movie_services.update_user_movie_rating(
        db, movie_id, current_user_id, movie.rating
    )


# @router.get(
#     path='/{movie_id}',
#     status_code=status.HTTP_200_OK,
#     response_model=MovieDetailSchema,
#     summary='Get a movie detail'
# )
# async def get_movie(db: Session, movie_id: int):
#     return await movie_services.get_movie_detail(db, movie_id)
