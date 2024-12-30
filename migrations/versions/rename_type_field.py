
"""Rename type to transaction_type in transactions

Revision ID: rename_type_field
Revises: add_username_column
Create Date: 2024-01-29 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'rename_type_field'
down_revision = 'add_username_column'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('transactions', 'type', new_column_name='transaction_type')

def downgrade():
    op.alter_column('transactions', 'transaction_type', new_column_name='type')
