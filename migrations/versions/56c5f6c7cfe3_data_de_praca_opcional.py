"""Data de praca opcional

Revision ID: 56c5f6c7cfe3
Revises: 3d5e7f9a1b20
"""

from alembic import op
import sqlalchemy as sa


revision = "56c5f6c7cfe3"
down_revision = "3d5e7f9a1b20"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("militares", schema=None) as batch_op:
        batch_op.alter_column(
            "data_de_praca",
            existing_type=sa.Date(),
            nullable=True
        )


def downgrade():
    with op.batch_alter_table("militares", schema=None) as batch_op:
        batch_op.alter_column(
            "data_de_praca",
            existing_type=sa.Date(),
            nullable=False
        )