from datetime import date

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app import app
from src.core.database import get_session
from src.models import Actor, Base, Movie, User, UserMovie


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


@pytest_asyncio.fixture
async def movie(session):
    movie = Movie(
        name='test_movie',
        synopsis='test_synopsis',
        director='test_director',
        release_date=date(2000, 1, 1),
    )
    session.add(movie)
    await session.commit()
    await session.refresh(movie)

    return movie


@pytest_asyncio.fixture
async def actor(session):
    actor = Actor(
        name='test_actor',
        age=18,
    )
    session.add(actor)
    await session.commit()
    await session.refresh(actor)

    return actor


@pytest_asyncio.fixture
async def other_actor(session):
    actor = Actor(
        name='test_other_actor',
        age=18,
    )
    session.add(actor)
    await session.commit()
    await session.refresh(actor)

    return actor


@pytest_asyncio.fixture
async def movie_rated(session, movie, user):
    movie_rated = UserMovie(user_id=user.id, movie_id=movie.id, rating=10)
    session.add(movie_rated)
    await session.commit()
    await session.refresh(movie_rated)

    return movie_rated
