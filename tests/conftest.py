import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app import app
from src.core.database import get_session
from src.models import Base, User


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory:',
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session):
    user = User(
        name='test_user',
        email='test_user@email.com',
        age=18,
        password='Teste123@',  # NOSONAR
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def other_user(session):
    user = User(
        name='test_other_user',
        email='test_other_user@email.com',
        age=18,
        password='Teste123@',  # NOSONAR
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
