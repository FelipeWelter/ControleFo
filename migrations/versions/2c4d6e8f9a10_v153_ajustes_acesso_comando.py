"""v153 ajustes acesso comando e secoes especiais

Revision ID: 2c4d6e8f9a10
Revises: 1b2c3d4e5f60
Create Date: 2026-07-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '2c4d6e8f9a10'
down_revision = '1b2c3d4e5f60'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    for nome in ("Comandante", "Subcomandante"):
        existe = conn.execute(sa.text("SELECT id FROM secoes WHERE nome = :nome"), {"nome": nome}).fetchone()
        if not existe:
            conn.execute(sa.text("INSERT INTO secoes (nome) VALUES (:nome)"), {"nome": nome})


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM secoes WHERE nome IN ('Comandante', 'Subcomandante')"))
