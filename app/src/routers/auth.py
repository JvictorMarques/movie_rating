from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models import User
from src.schemas.auth import LoginRequest, Token
from src.services import auth as auth_services

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(auth_services.get_current_user)]


@router.post(
    path='/token',
    status_code=status.HTTP_200_OK,
    response_model=Token,
    summary='Create access token',
)
async def token(
    db: Session,
    login_data: LoginRequest,
):
    return await auth_services.create_access_token(db, login_data)


@router.post(
    path='/refresh_token',
    status_code=status.HTTP_200_OK,
    response_model=Token,
    summary='Refresh access token',
)
async def refresh_token(current_user: CurrentUser):
    return auth_services.refresh_access_token(current_user)
