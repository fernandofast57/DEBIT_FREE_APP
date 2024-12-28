
from app import create_app
from app.models.models import db, User, MoneyAccount, GoldAccount, NobleRank

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

if __name__ == '__main__':
    init_db()
