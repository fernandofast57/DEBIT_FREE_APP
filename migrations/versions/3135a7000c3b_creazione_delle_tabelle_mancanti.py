
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3135a7000c3b'
down_revision = 'dc45cb3ac83f'
branch_labels = None
depends_on = None

def upgrade():
    # Creazione della tabella users se non esiste
    if not op.get_bind().dialect.has_table(op.get_bind(), 'users'):
        op.create_table(
            'users',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('username', sa.String(255), nullable=False),
            sa.Column('email', sa.String(255), nullable=False),
            sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
        )

    # Creazione della tabella transformations se non esiste
    if not op.get_bind().dialect.has_table(op.get_bind(), 'transformations'):
        op.create_table(
            'transformations',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
            sa.Column('amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('status', sa.String(50), nullable=False),
            sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
        )

    # Creazione della tabella transactions
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )

    # Creazione della tabella noble_ranks
    op.create_table(
        'noble_ranks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('rank_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )

    # Creazione della tabella noble_relations
    op.create_table(
        'noble_relations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('noble_rank_id', sa.Integer, sa.ForeignKey('noble_ranks.id')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )

def downgrade():
    # Rimozione delle tabelle in caso di rollback
    op.drop_table('noble_relations')
    op.drop_table('noble_ranks')
    op.drop_table('transactions')
    op.drop_table('users')
