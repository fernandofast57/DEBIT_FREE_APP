from app import create_app, db
from decimal import Decimal
from app.models.models import User # Assuming User model exists

# Assuming a NobleRank model exists or needs to be created.  This is a placeholder.  Replace with your actual database model.
class NobleRank:
    def __init__(self, rank_name, bonus_rate, min_investment, level):
        self.rank_name = rank_name
        self.bonus_rate = bonus_rate
        self.min_investment = min_investment
        self.level = level


def init_noble_ranks():
    app = create_app()
    with app.app_context():
        # Ensure tables exist (assuming a NobleRank table is created)
        db.create_all()

        # Initialize default noble ranks with bonus rates
        ranks = [
            NobleRank(rank_name='baron', bonus_rate=Decimal('0.000'), min_investment=Decimal('1000.00'), level=1),
            NobleRank(rank_name='count', bonus_rate=Decimal('0.007'), min_investment=Decimal('5000.00'), level=2),
            NobleRank(rank_name='duke', bonus_rate=Decimal('0.005'), min_investment=Decimal('10000.00'), level=3),
            NobleRank(rank_name='prince', bonus_rate=Decimal('0.005'), min_investment=Decimal('25000.00'), level=4)
        ]
        for rank in ranks:
            # Assuming appropriate database interaction for NobleRank.  Replace with your actual code.
            print(f"Initializing {rank.rank_name} rank with {rank.bonus_rate:.1%} bonus...")
            # Example database interaction (replace with your ORM):
            # new_rank = NobleRankModel(rank_name=rank.rank_name, bonus_rate=rank.bonus_rate, min_investment=rank.min_investment, level=rank.level)
            # db.session.add(new_rank)

        db.session.commit()

if __name__ == '__main__':
    init_noble_ranks()