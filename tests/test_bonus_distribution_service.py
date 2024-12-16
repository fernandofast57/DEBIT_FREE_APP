import unittest
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount
from app.models.noble_system import NobleRank, NobleRelation, BonusTransaction
from app.services.bonus_distribution_service import BonusDistributionService

class TestBonusDistributionService(unittest.TestCase):
    def setUp(self):
        # Crea app di test
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Crea database di test
        db.create_all()

        # Setup ranghi nobiliari
        self.nobile = NobleRank(title='Nobile', bonus_rate=Decimal('0.007'), level=1)
        self.visconte = NobleRank(title='Visconte', bonus_rate=Decimal('0.005'), level=2)
        self.conte = NobleRank(title='Conte', bonus_rate=Decimal('0.005'), level=3)

        db.session.add_all([self.nobile, self.visconte, self.conte])
        db.session.commit()

        # Setup utenti test
        self.user1 = User(email='user1@test.com')  # Utente base
        self.user2 = User(email='user2@test.com')  # Upline livello 1
        self.user3 = User(email='user3@test.com')  # Upline livello 2
        self.user4 = User(email='user4@test.com')  # Upline livello 3

        db.session.add_all([self.user1, self.user2, self.user3, self.user4])
        db.session.commit()

        # Setup conti denaro
        self.accounts = [
            MoneyAccount(user_id=user.id, balance=Decimal('0'))
            for user in [self.user1, self.user2, self.user3, self.user4]
        ]
        db.session.add_all(self.accounts)
        db.session.commit()

        # Setup relazioni affiliazione
        self.relations = [
            NobleRelation(referred_id=self.user1.id, referrer_id=self.user2.id, rank_id=self.nobile.id),
            NobleRelation(referred_id=self.user2.id, referrer_id=self.user3.id, rank_id=self.visconte.id),
            NobleRelation(referred_id=self.user3.id, referrer_id=self.user4.id, rank_id=self.conte.id)
        ]
        db.session.add_all(self.relations)
        db.session.commit()

        # Inizializza servizio
        self.service = BonusDistributionService()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_bonus_distribution(self):
        """Test distribuzione bonus su tre livelli"""
        transaction_amount = Decimal('1000')
        result = self.service.distribute_transaction_bonus(self.user1.id, transaction_amount)

        self.assertEqual(result['status'], 'success')

        # Verifica numero di distribuzioni
        self.assertEqual(len(result['distributions']), 3)

        # Verifica importi bonus
        distributions = result['distributions']

        # Primo livello - Nobile (0.7%)
        self.assertEqual(distributions[0]['user_id'], self.user2.id)
        self.assertAlmostEqual(distributions[0]['bonus_amount'], 7.0)

        # Secondo livello - Visconte (0.5%)
        self.assertEqual(distributions[1]['user_id'], self.user3.id)
        self.assertAlmostEqual(distributions[1]['bonus_amount'], 5.0)

        # Terzo livello - Conte (0.5%)
        self.assertEqual(distributions[2]['user_id'], self.user4.id)
        self.assertAlmostEqual(distributions[2]['bonus_amount'], 5.0)

        # Verifica saldi aggiornati
        accounts = MoneyAccount.query.all()
        for account in accounts:
            if account.user_id == self.user2.id:
                self.assertAlmostEqual(float(account.balance), 7.0)
            elif account.user_id == self.user3.id:
                self.assertAlmostEqual(float(account.balance), 5.0)
            elif account.user_id == self.user4.id:
                self.assertAlmostEqual(float(account.balance), 5.0)

    def test_no_upline(self):
        """Test distribuzione bonus senza upline"""
        # Crea un utente senza upline
        lone_user = User(email='lone@test.com')
        db.session.add(lone_user)
        db.session.flush()  # Questo assicura che lone_user abbia un id prima di usarlo

        lone_account = MoneyAccount(
            user_id=lone_user.id,  # Ora siamo sicuri che lone_user.id esista
            balance=Decimal('0')
        )
        db.session.add(lone_account)
        db.session.commit()

        result = self.service.distribute_transaction_bonus(
            lone_user.id, 
            Decimal('1000')
        )

        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['distributions']), 0)
        self.assertIn('Nessun upline trovato', result['message'])

    def test_bonus_history(self):
        """Test recupero storico bonus"""
        # Prima crea alcune transazioni bonus
        transaction_amount = Decimal('1000')
        self.service.distribute_transaction_bonus(self.user1.id, transaction_amount)

        # Recupera storico per user2 (primo upline)
        result = self.service.get_user_bonus_history(self.user2.id)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['history']), 1)

        bonus_tx = result['history'][0]
        self.assertEqual(float(bonus_tx['transaction_amount']), 1000.0)
        self.assertAlmostEqual(float(bonus_tx['bonus_amount']), 7.0)

if __name__ == '__main__':
    unittest.main()