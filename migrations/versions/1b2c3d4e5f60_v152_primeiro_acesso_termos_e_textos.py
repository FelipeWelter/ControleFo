"""v152 primeiro acesso termos e ajustes de interface

Revision ID: 1b2c3d4e5f60
Revises: c9f2a7401b8d
Create Date: 2026-07-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '1b2c3d4e5f60'
down_revision = 'c9f2a7401b8d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('primeiro_acesso', sa.Boolean(), nullable=False, server_default=sa.text('1')))
        batch_op.add_column(sa.Column('aceitou_termos', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        batch_op.add_column(sa.Column('data_aceite_termos', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('data_aceite_termos')
        batch_op.drop_column('aceitou_termos')
        batch_op.drop_column('primeiro_acesso')
