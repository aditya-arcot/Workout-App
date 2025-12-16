from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import TEXT, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from .exercise import Exercise


class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    exercises: Mapped[List["Exercise"]] = relationship(
        secondary="exercise_muscle_groups",
        back_populates="muscle_groups",
    )
