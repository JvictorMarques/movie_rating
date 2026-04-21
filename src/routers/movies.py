from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.movies import MovieCreateResponseSchema, MovieCreateSchema
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
