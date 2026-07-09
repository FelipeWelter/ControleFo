"""v154 solicitacao reset senha

Revision ID: 3d5e7f9a1b20
Revises: 2c4d6e8f9a10
"""

from alembic import op
import sqlalchemy as sa


revision = "3d5e7f9a1b20"
down_revision = "2c4d6e8f9a10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "solicitacoes_reset_senha",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("identidade_informada", sa.String(length=30), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("ip", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDENTE"),
        sa.Column("solicitado_em", sa.DateTime(), nullable=False),
        sa.Column("analisado_em", sa.DateTime(), nullable=True),
        sa.Column("analisado_por_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["analisado_por_id"], ["usuarios.id"], ondelete="SET NULL"),
    )


def downgrade():
    op.drop_table("solicitacoes_reset_senha")