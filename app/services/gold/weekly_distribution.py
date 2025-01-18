from decimal import Decimal
from datetime import datetime
import asyncio
from typing import Dict
from app.database import db
from app.models.distribution import WeeklyDistributionLog, DistributionSnapshot
from .distribution_backup import DistributionBackup
from .distribution_validator import DistributionValidator
from app.prometheus_config import track_distribution_metrics


class WeeklyGoldDistribution:

    def __init__(self):
        self.structure_fee = Decimal('0.05')  # 5%
        self.affiliate_fees = {
            1: Decimal('0.007'),  # 0.7%
            2: Decimal('0.005'),  # 0.5%
            3: Decimal('0.005')  # 0.5%
        }
        self.processing_lock = asyncio.Lock()
        self.validator = DistributionValidator()
        self.backup = DistributionBackup()

    async def pre_distribution_checks(self) -> bool:
        """Verifiche di sicurezza pre-distribuzione"""
        try:
            if datetime.now().weekday() != 1:  # 1 = Martedì
                raise ValueError(
                    "La distribuzione può essere eseguita solo il martedì")

            if datetime.now().hour < 15:  # Prima delle 15:00
                raise ValueError(
                    "La distribuzione può essere eseguita solo dopo il fixing (15:00)"
                )

            if not await self.validator.validate_system_status():
                raise SystemError("Sistema non pronto per la distribuzione")

            return True

        except Exception as e:
            await self.log_error("Pre-distribution check fallito", str(e))
            return False

    async def distribute_gold(self, user_id: int,
                              gold_amount: Decimal) -> bool:
        """Distribuisce l'oro a un singolo utente"""
        try:
            async with db.session() as session:
                # Aggiorna gold_account
                await session.execute(
                    """
                    UPDATE gold_accounts 
                    SET balance = balance + :gold_amount 
                    WHERE user_id = :user_id
                    """, {
                        'gold_amount': gold_amount,
                        'user_id': user_id
                    })

                # Azzera money_account
                await session.execute(
                    """
                    UPDATE money_accounts 
                    SET balance = 0 
                    WHERE user_id = :user_id
                    """, {'user_id': user_id})

                await session.commit()
                return True

        except Exception as e:
            await self.log_error("Errore nella distribuzione oro", str(e))
            return False

    async def distribute_affiliate_bonuses(self, user_id: int,
                                           gold_amount: Decimal) -> Dict:
        """Distribuisce i bonus di affiliazione"""
        distributed_amounts = {}
        try:
            async with db.session() as session:
                current_user_id = user_id

                for level, percentage in self.affiliate_fees.items():
                    # Trova il referrer
                    referrer = await session.execute(
                        "SELECT referrer_id FROM users WHERE id = :user_id",
                        {'user_id': current_user_id})
                    referrer_id = referrer.scalar()

                    if not referrer_id:
                        break

                    bonus_amount = gold_amount * percentage

                    # Aggiorna il gold_account del referrer
                    await session.execute(
                        """
                        UPDATE gold_accounts 
                        SET balance = balance + :bonus_amount 
                        WHERE user_id = :referrer_id
                        """, {
                            'bonus_amount': bonus_amount,
                            'referrer_id': referrer_id
                        })

                    distributed_amounts[f'level_{level}'] = float(bonus_amount)
                    current_user_id = referrer_id

                await session.commit()
                return distributed_amounts

        except Exception as e:
            await self.log_error("Errore nella distribuzione bonus", str(e))
            return {}

    @track_distribution_metrics
    async def process_distribution(self, fixing_price: Decimal) -> Dict:
        """Processo principale di distribuzione settimanale"""
        try:
            async with self.processing_lock:
                if not await self.pre_distribution_checks():
                    raise ValueError("Verifiche preliminari fallite")

                if not await self.validator.validate_fixing_price(fixing_price
                                                                  ):
                    raise ValueError("Prezzo fixing non valido")
                if fixing_price <= Decimal('0'):
                    raise ValueError("Fixing price must be positive")

                # Crea snapshot pre-distribuzione
                await self.backup.create_snapshot()

                total_euro = Decimal('0')
                total_gold = Decimal('0')
                total_affiliate_bonus = Decimal('0')
                processed_users = 0

                async with db.session() as session:
                    # Ottieni tutti gli utenti con saldo positivo
                    users = await session.execute(
                        "SELECT id, money_account_balance FROM users WHERE money_account_balance > 0"
                    )

                    for user_id, balance in users:
                        # Calcola oro al netto della fee struttura
                        net_amount = balance * (1 - self.structure_fee)
                        gold_amount = net_amount / fixing_price

                        # Distribuisci oro all'utente
                        if not await self.distribute_gold(
                                user_id, gold_amount):
                            raise Exception(
                                f"Errore distribuzione oro per user {user_id}")

                        # Distribuisci bonus affiliazione
                        affiliate_distribution = await self.distribute_affiliate_bonuses(
                            user_id, gold_amount)
                        total_affiliate_bonus += sum(
                            Decimal(str(x))
                            for x in affiliate_distribution.values())

                        total_euro += balance
                        total_gold += gold_amount
                        processed_users += 1

                    # Log della distribuzione
                    log = WeeklyDistributionLog(
                        processing_date=datetime.utcnow(),
                        fixing_price=fixing_price,
                        total_euro_processed=total_euro,
                        total_gold_distributed=total_gold,
                        total_affiliate_bonus=total_affiliate_bonus,
                        users_processed=processed_users,
                        status='completed')
                    session.add(log)
                    await session.commit()

                return {
                    'status': 'success',
                    'total_euro': float(total_euro),
                    'total_gold': float(total_gold),
                    'total_affiliate_bonus': float(total_affiliate_bonus),
                    'users_processed': processed_users,
                    'fixing_price': float(fixing_price)
                }

        except Exception as e:
            await self.log_error("Errore nel processo di distribuzione",
                                 str(e))
            await self.backup.restore_latest_snapshot()
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def log_error(self, message: str, error_details: str) -> None:
        """Logga gli errori nel database e notifica gli amministratori"""
        try:
            async with db.session() as session:
                log = WeeklyDistributionLog(processing_date=datetime.utcnow(),
                                            status='error',
                                            error_details={
                                                'message': message,
                                                'details': error_details
                                            })
                session.add(log)
                await session.commit()

            # Qui implementare la notifica agli amministratori
            # TODO: Implementare sistema di notifica

        except Exception as e:
            print(f"Errore nel logging: {str(e)}")  # Fallback logging