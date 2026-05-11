import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import EmailStr, SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import security
from src.core.constants import FORBIDDEN, USER_NOT_FOUND
from src.core.database import get_session
from src.models.users import User
from src.repositories import users as users_repository
from src.schemas.auth import LoginRequest, Token

bearer = HTTPBearer()
Credentials = Annotated[HTTPAuthorizationCredentials, Depends(bearer)]
Session = Annotated[AsyncSession, Depends(get_session)]

logger = logging.getLogger(__name__)


async def authenticate_user(
    db: AsyncSession, email: EmailStr, password: SecretStr
) -> User | None:
    user = await users_repository.get_user_by_email(db, email)
    if not user:
        return None
    if not security.verify_password(password, SecretStr(user.password)):
        return None
    return user


async def get_current_user(db: Session, credentials: Credentials) -> User:
    payload = security.verify_access_token(credentials.credentials)

    user_id_str = payload.get('sub')
    if not user_id_str:
        logger.warning('Token missing sub claim')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        logger.warning(
            'Token sub claim is not a valid integer',
            extra={'sub': user_id_str},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = await users_repository.get_user(db, user_id)
    if not user:
        logger.warning(
            'Authenticated token references non-existent user',
            extra={'user_id': user_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )

    logger.debug('User authenticated via token', extra={'user_id': user_id})
    return user


def verify_user_ownership(user: User, user_id: int) -> None:
    if user.id != user_id:
        logger.warning(
            FORBIDDEN,
            extra={'requesting_user_id': user.id, 'target_user_id': user_id},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=FORBIDDEN,
        )


async def create_access_token(
    db: AsyncSession, login_data: LoginRequest
) -> Token:
    user = await authenticate_user(db, login_data.email, login_data.password)

    if not user:
        logger.warning(
            'Failed login attempt', extra={'email': login_data.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = security.create_access_token(data={'sub': str(user.id)})
    logger.info('User logged in', extra={'user_id': user.id})
    return Token(access_token=access_token, token_type='bearer')


def refresh_access_token(current_user: User) -> Token:
    access_token = security.create_access_token(
        data={'sub': str(current_user.id)}
    )
    logger.debug('Token refreshed', extra={'user_id': current_user.id})
    return Token(access_token=access_token, token_type='bearer')
