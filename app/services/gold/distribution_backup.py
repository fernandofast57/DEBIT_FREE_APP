
from typing import Dict
from decimal import Decimal
from datetime import datetime
from app.database import db
from app.models.distribution import DistributionSnapshot

class DistributionBackup:
    async def create_snapshot(self) -> int:
        async with db.session() as session:
            query = """
                SELECT u.id, ma.balance as euro_balance, ga.balance as gold_balance
                FROM users u
                JOIN money_accounts ma ON ma.user_id = u.id
                JOIN gold_accounts ga ON ga.user_id = u.id
            """
            result = await session.execute(query)
            snapshot_data = {str(id): {'euro': str(euro), 'gold': str(gold)} 
                           for id, euro, gold in result}
            
            snapshot = DistributionSnapshot(
                timestamp=datetime.utcnow(),
                snapshot_data=snapshot_data
            )
            session.add(snapshot)
            await session.commit()
            return snapshot.id

    async def restore_latest_snapshot(self):
        async with db.session() as session:
            snapshot = await session.execute(
                """
                SELECT * FROM distribution_snapshots 
                WHERE restored = false 
                ORDER BY timestamp DESC LIMIT 1
                """
            )
            if snapshot:
                for user_id, data in snapshot.snapshot_data.items():
                    await session.execute(
                        """
                        UPDATE money_accounts 
                        SET balance = :euro 
                        WHERE user_id = :user_id
                        """,
                        {'euro': data['euro'], 'user_id': user_id}
                    )
                    await session.execute(
                        """
                        UPDATE gold_accounts 
                        SET balance = :gold 
                        WHERE user_id = :user_id
                        """,
                        {'gold': data['gold'], 'user_id': user_id}
                    )
                
                snapshot.restored = True
                await session.commit()
