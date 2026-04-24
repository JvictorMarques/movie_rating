from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.movies import (
    MovieCreateRatingResponseSchema,
    MovieCreateResponseSchema,
    MovieCreateSchema,
    MovieDetailSchema,
    MovieListSchema,
    MovieRatingSchema,
    MovieRatingUpdateResponseSchema,
    MovieUpdateResponseSchema,
    MovieUpdateSchema,
)
from src.services import movies as movie_services

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=MovieListSchema,
    summary='List movies',
)
async def list_movies(
    db: Session,
    limit: Annotated[
        int, Query(ge=1, le=100, description='Number maximum of records')
    ] = 100,
    offset: Annotated[int, Query(ge=0, description='Page number')] = 0,
    name_filter: Annotated[
        Optional[str], Query(description='Search filter by movie_name')
    ] = None,
    rating_filter: Annotated[
        Optional[float], Query(description='Search filter by rating')
    ] = None,
):
    return await movie_services.list_movies(
        db, limit, offset, name_filter, rating_filter
    )


@router.get(
    path='/{movie_id}',
    status_code=status.HTTP_200_OK,
    response_model=MovieDetailSchema,
    summary='Get a movie detail',
)
async def get_movie(db: Session, movie_id: int):
    return await movie_services.get_movie(db, movie_id)


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
    path='/{movie_id}',
    status_code=status.HTTP_200_OK,
    response_model=MovieUpdateResponseSchema,
    summary='Update movie information',
)
async def update_movie(db: Session, movie_id: int, movie: MovieUpdateSchema):
    return await movie_services.update_movie(db, movie_id, movie)


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


@router.delete(
    path='/{movie_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete a movie',
)
async def delete_movie(db: Session, movie_id: int):
    await movie_services.delete_movie(db, movie_id)
