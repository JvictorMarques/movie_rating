from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.movies import Movie
    from src.models.users import User


class UserMovie(Base):
    __tablename__ = 'users_movies'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), primary_key=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True
    )
    rating: Mapped[Optional[float]] = mapped_column(default=None)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped['User'] = relationship(back_populates='movies')
    movie: Mapped['Movie'] = relationship(back_populates='users')
