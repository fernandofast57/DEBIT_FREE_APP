
"""create_missing_tables

Revision ID: 3135a7000c3b
Revises: c564559997be
Create Date: 2024-01-24 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '3135a7000c3b'
down_revision = 'c564559997be'
branch_labels = None
depends_on = None

def upgrade():
    # Create missing tables
    with op.batch_alter_table('gold_transformations') as batch_op:
        batch_op.add_column(sa.Column('blockchain_tx_hash', sa.String(66), nullable=True))
        batch_op.add_column(sa.Column('blockchain_status', sa.String(20), server_default='pending'))

def downgrade():
    with op.batch_alter_table('gold_transformations') as batch_op:
        batch_op.drop_column('blockchain_tx_hash')
        batch_op.drop_column('blockchain_status')
