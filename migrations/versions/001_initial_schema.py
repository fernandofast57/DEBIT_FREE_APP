
"""Initial schema creation

Revision ID: 001_initial_schema
Revises: None
Create Date: 2024-01-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table first
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create email index
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Create money_accounts table
    op.create_table(
        'money_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), default=0),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create gold_accounts table
    op.create_table(
        'gold_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=4), default=0),
        sa.Column('last_update', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create noble_ranks table
    op.create_table(
        'noble_ranks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rank_name', sa.String(50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('gold_accounts')
    op.drop_table('money_accounts')
    op.drop_table('noble_ranks')
    op.drop_table('users')
"""Initial database schema

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum

def upgrade():
    # Create users table first
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(length=128)),
        sa.Column('referrer_id', sa.Integer()),
        sa.ForeignKeyConstraint(['referrer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create money_accounts table
    op.create_table('money_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), default=0),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create gold_accounts table
    op.create_table('gold_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=4), default=0),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('gold_accounts')
    op.drop_table('money_accounts')
    op.drop_table('users')
