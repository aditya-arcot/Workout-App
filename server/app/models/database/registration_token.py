from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class RegistrationToken(Base):
    __tablename__ = "registration_tokens"
    __table_args__ = (
        Index("ix_registration_tokens_email", "email"),
        Index("ix_registration_tokens_access_request_id", "access_request_id"),
        Index("ix_registration_tokens_token_hash", "token_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    access_request_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "access_requests.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
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

    @property
    def is_used(self) -> bool:
        return self.used_at is not None
