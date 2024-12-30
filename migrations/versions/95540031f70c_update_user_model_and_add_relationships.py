
"""Update user model and add relationships

Revision ID: 95540031f70c
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # First check if users table exists before trying to drop it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'users' in tables:
        op.drop_table('users')
        
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(length=128)),
        sa.Column('referrer_id', sa.Integer()),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
