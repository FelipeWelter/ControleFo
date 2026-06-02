"""multiplas permissoes por usuario

Revision ID: 60da7cb0fadc
Revises: 645b878f643f
Create Date: 2026-06-01 23:35:20.844668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60da7cb0fadc'
down_revision = '645b878f643f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('permissoes', sa.Text(), nullable=True)
        )

    op.execute("""
        UPDATE usuarios
        SET permissoes = perfil
    """)

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.alter_column('permissoes', nullable=False)
        batch_op.drop_column('perfil')


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('perfil', sa.String(length=20), nullable=True)
        )

    op.execute("""
        UPDATE usuarios
        SET perfil = permissoes
    """)

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.alter_column('perfil', nullable=False)
        batch_op.drop_column('permissoes')
