from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional
from app.database import db

class DistributionValidator:
    def __init__(self):
        self.min_fixing_price = Decimal('0.01')
        self.max_fixing_price = Decimal('100000.00')  # Valore massimo ragionevole

    async def validate_fixing_price(self, fixing_price: Decimal) -> bool:
        """Valida il prezzo di fixing"""
        try:
            if not isinstance(fixing_price, Decimal):
                return False

            if fixing_price <= self.min_fixing_price or fixing_price >= self.max_fixing_price:
                return False

            return True

        except Exception as e:
            await self.log_error("Errore nella validazione del fixing", str(e))
            return False

    async def validate_system_status(self) -> bool:
        """Verifica che il sistema sia pronto per la distribuzione"""
        try:
            async with db.session() as session:
                # Verifica che non ci siano distribuzioni in corso
                active_distributions = await session.execute(
                    """
                    SELECT COUNT(*) 
                    FROM weekly_distribution_logs 
                    WHERE status = 'in_progress'
                    """
                )
                if active_distributions.scalar() > 0:
                    return False

                # Verifica integrità database
                if not await self.check_database_integrity():
                    return False

                return True

        except Exception as e:
            await self.log_error("Errore nella validazione dello stato sistema", str(e))
            return False

    async def check_database_integrity(self) -> bool:
        """Verifica l'integrità del database"""
        try:
            async with db.session() as session:
                # Verifica che ogni utente abbia entrambi gli account
                mismatched_accounts = await session.execute(
                    """
                    SELECT COUNT(*) 
                    FROM users u 
                    WHERE NOT EXISTS (
                        SELECT 1 FROM money_accounts ma WHERE ma.user_id = u.id
                    ) OR NOT EXISTS (
                        SELECT 1 FROM gold_accounts ga WHERE ga.user_id = u.id
                    )
                    """
                )
                if mismatched_accounts.scalar() > 0:
                    return False

                # Verifica che non ci siano saldi negativi
                negative_balances = await session.execute(
                    """
                    SELECT COUNT(*) 
                    FROM money_accounts 
                    WHERE balance < 0 
                    UNION ALL 
                    SELECT COUNT(*) 
                    FROM gold_accounts 
                    WHERE balance < 0
                    """
                )
                if sum(row[0] for row in negative_balances) > 0:
                    return False

                return True

        except Exception as e:
            await self.log_error("Errore nel controllo integrità database", str(e))
            return False

    async def validate_distribution_result(self, 
                                        initial_state: Dict, 
                                        final_state: Dict, 
                                        fixing_price: Decimal) -> bool:
        """Valida i risultati della distribuzione"""
        try:
            # Verifica che tutti i soldi siano stati convertiti
            total_money_before = sum(Decimal(str(v)) for v in initial_state['money_accounts'].values())
            total_money_after = sum(Decimal(str(v)) for v in final_state['money_accounts'].values())

            if total_money_after != 0:
                return False

            # Verifica la corretta conversione in oro
            expected_gold = (total_money_before * Decimal('0.95')) / fixing_price  # 95% dopo fee
            actual_gold = sum(Decimal(str(v)) for v in final_state['gold_accounts'].values())

            # Permettiamo una piccola differenza dovuta agli arrotondamenti
            if abs(expected_gold - actual_gold) > Decimal('0.00001'):
                return False

            return True

        except Exception as e:
            await self.log_error("Errore nella validazione risultati", str(e))
            return False

    async def log_error(self, message: str, error_details: str) -> None:
        """Logga gli errori di validazione"""
        try:
            print(f"Validation Error - {message}: {error_details}")
            # TODO: Implementare sistema di logging più robusto
        except:
            pass