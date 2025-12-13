from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from app.core.db import Base
from sqlalchemy import DateTime, ForeignKey, String, func, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .muscle_group import MuscleGroup
    from .workout_exercise import WorkoutExercise


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(TEXT)
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    muscle_group: Mapped["MuscleGroup"] = relationship(back_populates="exercises")
    workout_exercises: Mapped[List["WorkoutExercise"]] = relationship(
        back_populates="exercise",
        passive_deletes=True,
    )
