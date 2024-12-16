import unittest
import json
from decimal import Decimal
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.models.noble_system import NobleRank, NobleRelation

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Setup test user
        self.user = User(email='test@test.com')
        db.session.add(self.user)
        db.session.flush()

        # Setup accounts
        self.money_account = MoneyAccount(
            user_id=self.user.id,
            balance=Decimal('1000.00')
        )
        self.gold_account = GoldAccount(
            user_id=self.user.id,
            balance=Decimal('0')
        )
        db.session.add_all([self.money_account, self.gold_account])

        # Setup noble ranks
        self.ranks = [
            NobleRank(title='Nobile', bonus_rate=Decimal('0.007'), level=1),
            NobleRank(title='Visconte', bonus_rate=Decimal('0.005'), level=2),
            NobleRank(title='Conte', bonus_rate=Decimal('0.005'), level=3)
        ]
        db.session.add_all(self.ranks)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_transfer_api(self):
        """Test API bonifici"""
        # Test processo bonifico
        response = self.client.post('/api/v1/transfers/process',
            json={
                'user_id': self.user.id,
                'amount': 500.00
            },
            content_type='application/json'
        )

        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['transaction']['amount'], 500.00)

        # Test aggiunta al batch
        response = self.client.post('/api/v1/transfers/batch/add',
            json={
                'user_id': self.user.id,
                'amount': 300.00
            },
            content_type='application/json'
        )
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')

        # Test processo batch
        response = self.client.post('/api/v1/transfers/batch/process')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')

    def test_transformation_api(self):
        """Test API trasformazioni"""
        async def async_test():
            response = await self.client.post('/api/v1/transformations/transform',
                json={
                    'user_id': self.user.id,
                    'fixing_price': 1800.50
                },
                content_type='application/json'
            )
            return response
            
        response = self.loop.run_until_complete(async_test())
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')

        # Test storico trasformazioni
        response = self.client.get(f'/api/v1/transformations/history/{self.user.id}')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(isinstance(data['history'], list))

    def test_bonus_api(self):
        """Test API bonus"""
        # Setup upline per test bonus
        upline = User(email='upline@test.com')
        db.session.add(upline)
        db.session.flush()

        relation = NobleRelation(
            referred_id=self.user.id,
            referrer_id=upline.id,
            rank_id=self.ranks[0].id
        )
        db.session.add(relation)

        money_account = MoneyAccount(
            user_id=upline.id,
            balance=Decimal('0')
        )
        db.session.add(money_account)
        db.session.commit()

        # Test distribuzione bonus
        response = self.client.post('/api/v1/bonuses/distribute',
            json={
                'user_id': self.user.id,
                'transaction_amount': 1000.00
            },
            content_type='application/json'
        )
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')

        # Test storico bonus
        response = self.client.get(f'/api/v1/bonuses/history/{upline.id}')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(isinstance(data['history'], list))

    def test_invalid_inputs(self):
        """Test gestione input non validi"""
        # Test bonifico con amount non valido
        response = self.client.post('/api/v1/transfers/process',
            json={
                'user_id': self.user.id,
                'amount': 'invalid'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        # Test trasformazione con fixing price non valido
        response = self.client.post('/api/v1/transformations/transform',
            json={
                'user_id': self.user.id,
                'fixing_price': 'invalid'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()