
"""Update user model and add relationships

Revision ID: 95540031f70c
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

def table_exists(conn, table_name):
    inspector = Inspector.from_engine(conn)
    return table_name in inspector.get_table_names()

def upgrade():
    conn = op.get_bind()
    
    # Create users table
    if not table_exists(conn, 'users'):
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=50), nullable=False),
            sa.Column('email', sa.String(length=120), unique=True, nullable=False),
            sa.Column('password_hash', sa.String(length=128)),
            sa.PrimaryKeyConstraint('id')
        )

    # Create money_accounts table
    if not table_exists(conn, 'money_accounts'):
        op.create_table('money_accounts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('balance', sa.Numeric(precision=10, scale=2), default=0),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    conn = op.get_bind()
    if table_exists(conn, 'money_accounts'):
        op.drop_table('money_accounts')
    if table_exists(conn, 'users'):
        op.drop_table('users')
