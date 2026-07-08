"""v151 companhias e escopo de acesso

Revision ID: c9f2a7401b8d
Revises: a15c0f9d7b21
Create Date: 2026-07-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'c9f2a7401b8d'
down_revision = 'a15c0f9d7b21'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'companhias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('sigla', sa.String(length=30), nullable=True),
        sa.Column('ativa', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )

    with op.batch_alter_table('militares', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_companhia', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_militares_companhia',
            'companhias',
            ['id_companhia'],
            ['id']
        )

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nivel_acesso', sa.String(length=20), nullable=False, server_default='SECAO'))
        batch_op.add_column(sa.Column('companhia_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('secao_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_usuarios_companhia_escopo',
            'companhias',
            ['companhia_id'],
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_usuarios_secao_escopo',
            'secoes',
            ['secao_id'],
            ['id']
        )


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('fk_usuarios_secao_escopo', type_='foreignkey')
        batch_op.drop_constraint('fk_usuarios_companhia_escopo', type_='foreignkey')
        batch_op.drop_column('secao_id')
        batch_op.drop_column('companhia_id')
        batch_op.drop_column('nivel_acesso')

    with op.batch_alter_table('militares', schema=None) as batch_op:
        batch_op.drop_constraint('fk_militares_companhia', type_='foreignkey')
        batch_op.drop_column('id_companhia')

    op.drop_table('companhias')
