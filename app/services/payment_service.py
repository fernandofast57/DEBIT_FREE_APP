from decimal import Decimal
from app.models.models import Transaction, db

class PaymentService:
    PAYMENT_FEES = {
        'bank_transfer': Decimal('0.00'),
        'credit_card': Decimal('0.029'),  # 2.9%
        'paypal': Decimal('0.039')        # 3.9%
    }

    @staticmethod
    def calculate_processing_fee(amount: Decimal, payment_method: str) -> Decimal:
        """Calcola le commissioni di elaborazione in base al metodo di pagamento"""
        fee_percentage = PaymentService.PAYMENT_FEES.get(payment_method, Decimal('0'))
        return amount * fee_percentage

    @staticmethod
    async def process_payment(transaction: Transaction) -> bool:
        """Elabora il pagamento e applica le commissioni appropriate"""
        try:
            fee = PaymentService.calculate_processing_fee(transaction.amount, transaction.payment_method)
            transaction.processing_fee = fee
            transaction.calculate_net_amount()

            db.session.add(transaction)
            await db.session.commit()
            return True
        except Exception as e:
            await db.session.rollback()
            raise e

    @staticmethod # Added to match the original code style.  Instance method would require significant restructuring.
    async def process_gold_payment(amount: Decimal, user_id: int) -> dict:
        """Process gold payment transaction according to glossary definitions"""
        #Implementation for gold payment processing would go here.  This is a placeholder.
        #This needs to be fleshed out based on the actual glossary definitions.
        try:
          # Example:  Assume a gold transaction is a type of transaction.  Needs proper adaptation.
          transaction = Transaction(amount=amount, user_id=user_id, payment_method='gold')
          fee = PaymentService.calculate_processing_fee(transaction.amount, transaction.payment_method)
          transaction.processing_fee = fee
          transaction.calculate_net_amount()
          db.session.add(transaction)
          await db.session.commit()
          return {"status": "success"}
        except Exception as e:
            await db.session.rollback()
            return {"status": "failure", "error": str(e)}