"""creazione delle tabelle mancanti

Revision ID: 3135a7000c3b
Revises: dc45cb3ac83f
Create Date: 2024-01-10 13:53:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '3135a7000c3b'
down_revision = 'dc45cb3ac83f'
branch_labels = None
depends_on = None

def upgrade():
    # Verifica se le tabelle esistono prima di crearle
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'transactions' not in existing_tables:
        op.create_table(
            'transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Procedi con le altre tabelle...

def downgrade():
    # Il downgrade rimane invariato poiché drop_table fallisce silenziosamente se la tabella non esiste
    op.drop_table('transactions')
