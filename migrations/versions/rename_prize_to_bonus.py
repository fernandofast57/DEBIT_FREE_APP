
"""rename prize_transactions to bonus_transactions

Revision ID: rename_prize_to_bonus
Revises: add_blockchain_fields
Create Date: 2024-01-25 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'rename_prize_to_bonus'
down_revision = 'add_blockchain_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Rename table
    op.rename_table('prize_transactions', 'bonus_transactions')

def downgrade():
    # Revert table name
    op.rename_table('bonus_transactions', 'prize_transactions')
