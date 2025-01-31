from decimal import Decimal
from app import create_app, db
from app.models.models import NobleRank

def init_noble_ranks():
    app = create_app()
    with app.app_context():
        db.create_all()

        ranks = [
            NobleRank(
                level=1,
                bonus_rate=Decimal('0.007'),
                description='Premio del 0.7% in grammi dell\'oro acquisito dai referral diretti'
            ),
            NobleRank(
                level=2,
                bonus_rate=Decimal('0.005'),
                description='Premio del 0.5% in grammi dell\'oro acquisito dai referral indiretti'
            ),
            NobleRank(
                level=3,
                bonus_rate=Decimal('0.005'),
                description='Premio del 0.5% in grammi dell\'oro acquisito dai referral di terzo livello'
            )
        ]

        for rank in ranks:
            existing = NobleRank.query.filter_by(rank_name=rank.rank_name).first()
            if not existing:
                db.session.add(rank)
                print(f"Initializing {rank.rank_name} rank with {float(rank.bonus_rate)*100:.1f}% bonus rate and minimum investment of €{float(rank.min_investment):,.2f}")

        db.session.commit()

if __name__ == '__main__':
    init_noble_ranks()