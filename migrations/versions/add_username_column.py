
"""Add username column to users table

Revision ID: add_username_column
Revises: 95540031f70c
Create Date: 2024-01-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_username_column'
down_revision = '95540031f70c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('username', sa.String(50), nullable=False))
    op.create_unique_constraint('uq_users_username', 'users', ['username'])

def downgrade():
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.drop_column('users', 'username')
