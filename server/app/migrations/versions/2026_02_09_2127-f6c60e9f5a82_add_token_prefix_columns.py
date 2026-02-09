"""add token prefix columns

Revision ID: f6c60e9f5a82
Revises: 1b384d4d04c8
Create Date: 2026-02-09 21:27:00.000000-06:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f6c60e9f5a82"
down_revision: Union[str, Sequence[str], None] = "1b384d4d04c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add token_prefix column to password_reset_tokens table
    op.add_column(
        "password_reset_tokens",
        sa.Column("token_prefix", sa.String(length=12), nullable=True),
    )
    
    # Create index on token_prefix for fast lookups
    op.create_index(
        "ix_password_reset_tokens_token_prefix",
        "password_reset_tokens",
        ["token_prefix"],
        unique=False,
    )

    # Add token_prefix column to registration_tokens table
    op.add_column(
        "registration_tokens",
        sa.Column("token_prefix", sa.String(length=12), nullable=True),
    )
    
    # Create index on token_prefix for fast lookups
    op.create_index(
        "ix_registration_tokens_token_prefix",
        "registration_tokens",
        ["token_prefix"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop index and column from registration_tokens
    op.drop_index(
        "ix_registration_tokens_token_prefix", table_name="registration_tokens"
    )
    op.drop_column("registration_tokens", "token_prefix")

    # Drop index and column from password_reset_tokens
    op.drop_index(
        "ix_password_reset_tokens_token_prefix", table_name="password_reset_tokens"
    )
    op.drop_column("password_reset_tokens", "token_prefix")
