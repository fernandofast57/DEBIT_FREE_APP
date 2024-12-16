import unittest
from decimal import Decimal
from app import create_app, db
from app.services.batch_collection_service import BatchCollectionService
from app.models.models import User, MoneyAccount, Transaction

class TestBatchCollectionService(unittest.TestCase):
    def setUp(self):
        # Crea un'app di test
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Crea il database di test
        db.create_all()

        # Setup test user and account
        self.user = User(email='test@test.com')
        db.session.add(self.user)
        db.session.commit()

        self.money_account = MoneyAccount(user_id=self.user.id)
        db.session.add(self.money_account)
        db.session.commit()

        # Inizializza il servizio
        self.service = BatchCollectionService()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_process_bank_transfer(self):
        """Test processamento singolo bonifico"""
        result = self.service.process_bank_transfer(
            user_id=self.user.id,
            amount=Decimal('1000')
        )

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['transaction']['amount'], 1000.0)

        # Verifica saldo aggiornato
        self.assertEqual(float(self.money_account.balance), 1000.0)

        # Verifica transazione creata
        transaction = Transaction.query.first()
        self.assertIsNotNone(transaction)
        self.assertEqual(float(transaction.amount), 1000.0)

    def test_minimum_amount(self):
        """Test validazione importo minimo"""
        result = self.service.process_bank_transfer(
            user_id=self.user.id,
            amount=Decimal('50')  # Sotto il minimo di 100€
        )

        self.assertEqual(result['status'], 'error')
        self.assertIn('Importo minimo', result['message'])

    def test_weekly_batch_processing(self):
        """Test processamento batch settimanale"""
        # Aggiungi alcune transazioni al batch
        self.service.add_to_batch(self.user.id, Decimal('1000'))
        self.service.add_to_batch(self.user.id, Decimal('2000'))

        # Processa il batch
        result = self.service.process_weekly_batch()

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['summary']['total_processed'], 2)
        self.assertEqual(result['summary']['success_count'], 2)
        self.assertEqual(float(self.money_account.balance), 3000.0)

if __name__ == '__main__':
    unittest.main()