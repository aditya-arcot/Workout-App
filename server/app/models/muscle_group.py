from datetime import datetime
from typing import List, TYPE_CHECKING
from app.core.db import Base
from sqlalchemy import DateTime, String, func, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
        back_populates="muscle_group",
        passive_deletes=True,
    )
