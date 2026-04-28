from typing import Optional

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.schemas.users import UserCreateSchema


async def email_exists(db: AsyncSession, email: str) -> bool | None:
    return await db.scalar(select(exists().where(User.email == email)))


async def create_user(db: AsyncSession, user_data: UserCreateSchema) -> User:
    user = User(
        **user_data.model_dump(exclude={'password'}),
        password=user_data.password.get_secret_value(),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def list_all_users(
    db: AsyncSession, limit: int, offset: int, search_filter: Optional[str]
) -> list[User]:
    query = select(User).offset(offset).limit(limit)
    if search_filter:
        query = query.where(User.name.ilike(f'%{search_filter}%'))
    result = await db.scalars(query)
    return list(result.all())


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await db.get(User, user_id)
    await db.delete(user)
    await db.commit()


async def update_user(db: AsyncSession, user: User, update_data: dict) -> User:
    for key, value in update_data.items():
        if key == 'password':
            setattr(user, key, value.get_secret_value())
        else:
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


async def check_user_exists(db: AsyncSession, user_id: int) -> bool | None:
    return await db.scalar(select(exists().where(User.id == user_id)))


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
