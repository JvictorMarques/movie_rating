from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.actors import ActorCreateResponseSchema, ActorCreateSchema
from src.services import actors as actors_service

router = APIRouter()
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=ActorCreateResponseSchema,
    summary='Create an actor/actress',
)
async def create_actor(db: Session, actor: ActorCreateSchema):
    return await actors_service.create_actor(db, actor)


# TODO - Rate actors
# TODO - Update actors rating
# TODO - Update actors
# TODO - Get actors
# TODO - List actors
# TODO - Delete movies
