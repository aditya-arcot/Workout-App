"""update feedback table columms

Revision ID: 10750c61592f
Revises: 79347a71235f
Create Date: 2026-01-22 10:12:49.042346-06:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "10750c61592f"
down_revision: Union[str, Sequence[str], None] = "79347a71235f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "feedbacks", sa.Column("url", sa.TEXT(), nullable=False, server_default="")
    )
    op.add_column(
        "feedbacks", sa.Column("title", sa.TEXT(), nullable=False, server_default="")
    )
    op.add_column(
        "feedbacks",
        sa.Column("description", sa.TEXT(), nullable=False, server_default=""),
    )
    op.drop_column("feedbacks", "text")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "feedbacks", sa.Column("text", sa.TEXT(), autoincrement=False, nullable=False)
    )
    op.drop_column("feedbacks", "description")
    op.drop_column("feedbacks", "title")
    op.drop_column("feedbacks", "url")
