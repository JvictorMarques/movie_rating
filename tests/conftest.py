from datetime import date

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload

from app import app
from src.core.database import get_session
from src.models import Actor, Base, Movie, MovieActor, User, UserMovie


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

    await engine.dispose()


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


async def _load_movie_with_actors(
    session: AsyncSession, movie_id: int
) -> Movie:
    result = await session.execute(
        select(Movie)
        .where(Movie.id == movie_id)
        .options(selectinload(Movie.actors))
    )
    return result.scalar_one()


async def _load_movie_with_actors_rating(
    session: AsyncSession, movie_id: int
) -> Movie:
    result = await session.execute(
        select(Movie)
        .where(Movie.id == movie_id)
        .options(selectinload(Movie.actors), selectinload(Movie.user_movies))
    )
    return result.scalar_one()


@pytest_asyncio.fixture
async def movie(session, user, actor, other_actor):
    m = Movie(
        name='test_movie',
        synopsis='test_synopsis',
        director='test_director',
        release_date=date(2000, 1, 1),
    )
    session.add(m)
    await session.commit()
    await session.refresh(m)

    session.add(MovieActor(movie_id=m.id, actor_id=actor.id))
    session.add(MovieActor(movie_id=m.id, actor_id=other_actor.id))
    session.add(UserMovie(user_id=user.id, movie_id=m.id, rating=10))
    await session.commit()

    return await _load_movie_with_actors_rating(session, m.id)


@pytest_asyncio.fixture
async def movie_without_rating(session, actor, other_actor):
    m = Movie(
        name='test_movie_without_rating',
        synopsis='test_synopsis_without_rating',
        director='test_director_without_rating',
        release_date=date(2000, 1, 1),
    )
    session.add(m)
    await session.commit()
    await session.refresh(m)

    session.add(MovieActor(movie_id=m.id, actor_id=actor.id))
    session.add(MovieActor(movie_id=m.id, actor_id=other_actor.id))
    await session.commit()

    return await _load_movie_with_actors(session, m.id)


@pytest_asyncio.fixture
async def movie_without_cast(session, user):
    m = Movie(
        name='test_movie_without_cast',
        synopsis='test_synopsis_without_cast',
        director='test_director_without_cast',
        release_date=date(2000, 1, 1),
    )
    session.add(m)
    await session.commit()
    await session.refresh(m)

    session.add(UserMovie(user_id=user.id, movie_id=m.id, rating=10))
    await session.commit()

    return await _load_movie_with_actors(session, m.id)


@pytest_asyncio.fixture
async def movie_rated(session, movie_without_rating, user):
    movie_rated = UserMovie(
        user_id=user.id, movie_id=movie_without_rating.id, rating=10
    )
    session.add(movie_rated)
    await session.commit()
    await session.refresh(movie_rated)

    return movie_rated
