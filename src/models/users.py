from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models import Movie, UserMovie


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user_movies: Mapped[list['UserMovie']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    movies: Mapped[list['Movie']] = relationship(
        secondary='users_movies', viewonly=True
    )
