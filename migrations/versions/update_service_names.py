
"""update service names

Revision ID: update_service_names
Revises: rename_prize_to_bonus
Create Date: 2024-01-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_service_names'
down_revision = 'rename_prize_to_bonus'
branch_labels = None
depends_on = None

def upgrade():
    # Update service references in the database
    op.execute("UPDATE system_logs SET service_name = 'NotificationService' WHERE service_name = 'ServizioNotifiche'")
    op.execute("UPDATE system_logs SET service_name = 'KYCService' WHERE service_name = 'ServizioKyc'")
    op.execute("UPDATE system_logs SET service_name = 'AccountingService' WHERE service_name = 'ServizioContabilita'")

def downgrade():
    # Revert service names
    op.execute("UPDATE system_logs SET service_name = 'NotificationService' WHERE service_name = 'ServizioNotifiche'")
    op.execute("UPDATE system_logs SET service_name = 'KycService' WHERE service_name = 'ServizioKyc'")
    op.execute("UPDATE system_logs SET service_name = 'AccountingService' WHERE service_name = 'ServizioContabilita'")
