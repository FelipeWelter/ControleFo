"""Identidade militar opcional

Revision ID: 6a7b8c9d0e1f
Revises: 56c5f6c7cfe3
"""

from alembic import op
import sqlalchemy as sa


revision = "6a7b8c9d0e1f"
down_revision = "56c5f6c7cfe3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("militares", schema=None) as batch_op:
        batch_op.alter_column(
            "identidade_militar",
            existing_type=sa.String(length=30),
            nullable=True
        )


def downgrade():
    with op.batch_alter_table("militares", schema=None) as batch_op:
        batch_op.alter_column(
            "identidade_militar",
            existing_type=sa.String(length=30),
            nullable=False
        )
