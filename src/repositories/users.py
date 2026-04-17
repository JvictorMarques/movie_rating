from typing import Optional

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.schemas.users import UserSchema


async def email_exists(db: AsyncSession, email: str) -> bool | None:
    return await db.scalar(select(exists().where(User.email == email)))


async def create_user(db: AsyncSession, user_data: UserSchema) -> User:
    user = User(
        **user_data.model_dump(exclude={'password'}),
        password=user_data.password.get_secret_value(),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def list_all_users(
    db: AsyncSession, limit: int, offset: int, filter: Optional[str]
) -> list[User]:
    query = select(User).offset(offset).limit(limit)
    if filter:
        query = query.where(User.name.ilike(filter))
    result = await db.scalars(query)
    return list(result.all())


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await db.get(User, user_id)
    await db.delete(user)
    await db.commit()
