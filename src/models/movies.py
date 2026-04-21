from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.movies_actors import MovieActor
    from src.models.users_movies import UserMovie


class Movie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    synopsis: Mapped[Optional[str]] = mapped_column(Text)
    director: Mapped[str] = mapped_column(String(100), nullable=False)
    release_date: Mapped[date] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    users: Mapped[list['UserMovie']] = relationship(back_populates='movie')
    actors: Mapped[list['MovieActor']] = relationship(back_populates='movie')
