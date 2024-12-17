
from app import create_app, db
from app.models.models import User

def init_noble_ranks():
    app = create_app()
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Initialize default noble ranks
        ranks = ['noble', 'viscount', 'count']
        for rank in ranks:
            if not User.query.filter_by(noble_rank=rank).first():
                print(f"Initializing {rank} rank...")
                user = User(
                    email=f"{rank}@example.com",
                    noble_rank=rank
                )
                db.session.add(user)
        
        db.session.commit()

if __name__ == '__main__':
    init_noble_ranks()
