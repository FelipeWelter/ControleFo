"""grande atualizacao v150 dispensas

Revision ID: a15c0f9d7b21
Revises: 60da7cb0fadc
Create Date: 2026-07-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a15c0f9d7b21'
down_revision = '60da7cb0fadc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'dispensas_militares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('militar_id', sa.Integer(), nullable=False),
        sa.Column('registrado_por_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=120), nullable=False),
        sa.Column('data_inicio', sa.Date(), nullable=False),
        sa.Column('data_fim', sa.Date(), nullable=False),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('data_registro', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['militar_id'], ['militares.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['registrado_por_id'], ['usuarios.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('dispensas_militares')
