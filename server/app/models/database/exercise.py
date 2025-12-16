from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import TEXT, DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from .muscle_group import MuscleGroup
    from .user import User
    from .workout_exercise import WorkoutExercise


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        Index("ix_exercises_user_id", "user_id"),
        UniqueConstraint("user_id", "name", name="uq_exercises_user_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # null for system exercise
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    muscle_groups: Mapped[List["MuscleGroup"]] = relationship(
        secondary="exercise_muscle_groups",
        back_populates="exercises",
    )
    user: Mapped[Optional["User"]] = relationship(back_populates="exercises")
    workout_exercises: Mapped[List["WorkoutExercise"]] = relationship(
        back_populates="exercise",
        passive_deletes=True,
    )
