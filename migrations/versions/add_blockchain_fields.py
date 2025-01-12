
"""add blockchain fields

Revision ID: add_blockchain_fields
Revises: dc45cb3ac83f
Create Date: 2024-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_blockchain_fields'
down_revision = 'dc45cb3ac83f'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('gold_transformations', sa.Column('blockchain_tx_hash', sa.String(66), nullable=True))
    op.add_column('gold_transformations', sa.Column('blockchain_status', sa.String(20), server_default='pending'))

def downgrade():
    op.drop_column('gold_transformations', 'blockchain_tx_hash')
    op.drop_column('gold_transformations', 'blockchain_status')
