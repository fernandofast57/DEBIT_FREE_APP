from typing import Dict, Optional
from datetime import datetime
import json
from app.database import db
from app.models.distribution import DistributionSnapshot


class DistributionBackup:

    def __init__(self):
        self.backup_path = "backups/distribution"

    async def create_snapshot(self) -> int:
        """Crea uno snapshot dello stato corrente dei saldi"""
        try:
            snapshot_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'money_accounts': {},
                'gold_accounts': {}
            }

            async with db.session() as session:
                # Snapshot dei money accounts
                money_accounts = await session.execute("""
                    SELECT user_id, balance 
                    FROM money_accounts 
                    WHERE balance > 0
                    """)
                for user_id, balance in money_accounts:
                    snapshot_data['money_accounts'][str(user_id)] = str(
                        balance)

                # Snapshot dei gold accounts
                gold_accounts = await session.execute("""
                    SELECT user_id, balance 
                    FROM gold_accounts
                    """)
                for user_id, balance in gold_accounts:
                    snapshot_data['gold_accounts'][str(user_id)] = str(balance)

                # Salva lo snapshot nel database
                snapshot = DistributionSnapshot(timestamp=datetime.utcnow(),
                                                snapshot_data=snapshot_data,
                                                restored=False)
                session.add(snapshot)
                await session.commit()

                return snapshot.id

        except Exception as e:
            await self.log_error("Errore nella creazione dello snapshot",
                                 str(e))
            raise

    async def restore_latest_snapshot(self) -> bool:
        """Ripristina l'ultimo snapshot disponibile"""
        try:
            async with db.session() as session:
                # Trova l'ultimo snapshot non ripristinato
                latest_snapshot = await session.execute("""
                    SELECT id, snapshot_data 
                    FROM distribution_snapshots 
                    WHERE restored = false 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                    """)
                snapshot_id, snapshot_data = latest_snapshot.first()

                if not snapshot_data:
                    raise ValueError(
                        "Nessuno snapshot disponibile per il ripristino")

                # Ripristina i saldi dei money accounts
                for user_id, balance in snapshot_data['money_accounts'].items(
                ):
                    await session.execute(
                        """
                        UPDATE money_accounts 
                        SET balance = :balance 
                        WHERE user_id = :user_id
                        """, {
                            'balance': balance,
                            'user_id': int(user_id)
                        })

                # Ripristina i saldi dei gold accounts
                for user_id, balance in snapshot_data['gold_accounts'].items():
                    await session.execute(
                        """
                        UPDATE gold_accounts 
                        SET balance = :balance 
                        WHERE user_id = :user_id
                        """, {
                            'balance': balance,
                            'user_id': int(user_id)
                        })

                # Marca lo snapshot come ripristinato
                await session.execute(
                    """
                    UPDATE distribution_snapshots 
                    SET restored = true 
                    WHERE id = :snapshot_id
                    """, {'snapshot_id': snapshot_id})

                await session.commit()
                return True

        except Exception as e:
            await self.log_error("Errore nel ripristino dello snapshot",
                                 str(e))
            return False

    async def verify_snapshot_integrity(self, snapshot_id: int) -> bool:
        """Verifica l'integrità di uno snapshot"""
        try:
            async with db.session() as session:
                snapshot = await session.execute(
                    """
                    SELECT snapshot_data 
                    FROM distribution_snapshots 
                    WHERE id = :snapshot_id
                    """, {'snapshot_id': snapshot_id})
                snapshot_data = snapshot.scalar()

                if not snapshot_data:
                    return False

                # Verifica che tutti gli account necessari siano presenti
                money_accounts = set(snapshot_data['money_accounts'].keys())
                gold_accounts = set(snapshot_data['gold_accounts'].keys())

                if money_accounts != gold_accounts:
                    return False

                return True

        except Exception as e:
            await self.log_error("Errore nella verifica dello snapshot",
                                 str(e))
            return False

    async def log_error(self, message: str, error_details: str) -> None:
        """Logga gli errori relativi al backup"""
        try:
            print(f"Backup Error - {message}: {error_details}")
            # TODO: Implementare sistema di logging più robusto
        except:
            pass
