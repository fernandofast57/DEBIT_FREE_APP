from decimal import Decimal
import logging
from datetime import datetime
from typing import Dict, Optional
from app.database import db
from app.models.models import GoldAccount, EuroAccount, Transaction
from app.utils.blockchain_monitor import BlockchainMonitor
from app.utils.notification_service import NotificationService

class AutoRecoverySystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blockchain_monitor = BlockchainMonitor()
        self.notification_service = NotificationService()

    async def handle_inconsistency(self, account_id: int, error_type: str) -> bool:
        """Gestisce e corregge automaticamente le incongruenze"""
        try:
            # Backup dello stato prima del recovery
            pre_recovery_state = await self._create_snapshot(account_id)

            if error_type == "balance_mismatch":
                success = await self._handle_balance_mismatch(account_id)
            elif error_type == "failed_transaction":
                success = await self._handle_failed_transaction(account_id)
            elif error_type == "blockchain_sync":
                success = await self._handle_blockchain_sync(account_id)
            else:
                success = False

            if not success:
                await self._restore_snapshot(account_id, pre_recovery_state)
                await self.notification_service.notify_admins(
                    "CRITICAL_RECOVERY_FAILURE",
                    f"Recovery failed for account {account_id}"
                )

            return success

        except Exception as e:
            self.logger.critical(f"Recovery system error: {str(e)}")
            await self.notification_service.notify_admins(
                "CRITICAL_SYSTEM_ERROR",
                f"Recovery system failure: {str(e)}"
            )
            return False

    async def _create_snapshot(self, account_id: int) -> Dict:
        """Crea snapshot dello stato corrente"""
        async with db.session() as session:
            gold_account = await session.query(GoldAccount).filter_by(id=account_id).first()
            money_account = await session.query(EuroAccount).filter_by(id=account_id).first()

            return {
                'gold_balance': gold_account.balance if gold_account else Decimal('0'),
                'money_balance': money_account.balance if money_account else Decimal('0'),
                'timestamp': datetime.utcnow()
            }

    async def _restore_snapshot(self, account_id: int, snapshot: Dict) -> bool:
        """Ripristina lo stato da uno snapshot"""
        try:
            async with db.session() as session:
                gold_account = await session.query(GoldAccount).filter_by(id=account_id).first()
                money_account = await session.query(EuroAccount).filter_by(id=account_id).first()

                if gold_account:
                    gold_account.balance = snapshot['gold_balance']
                if money_account:
                    money_account.balance = snapshot['money_balance']

                await session.commit()
                return True

        except Exception as e:
            self.logger.error(f"Snapshot restore failed: {str(e)}")
            return False