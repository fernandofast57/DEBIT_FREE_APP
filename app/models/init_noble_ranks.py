from app import db, create_app
from app.models.noble_system import NobleRank
from decimal import Decimal

def init_noble_ranks():
    # Creiamo i ranghi nobiliari con le percentuali corrette
    ranks = [
        NobleRank(
            title='Nobile',
            bonus_rate=Decimal('0.007'),  # 0.7%
            level=1
        ),
        NobleRank(
            title='Visconte',
            bonus_rate=Decimal('0.005'),  # 0.5%
            level=2
        ),
        NobleRank(
            title='Conte',
            bonus_rate=Decimal('0.005'),  # 0.5%
            level=3
        )
    ]

    try:
        # Verifichiamo se i ranghi esistono già
        existing_ranks = NobleRank.query.all()
        if not existing_ranks:
            # Aggiungiamo i ranghi al database
            for rank in ranks:
                db.session.add(rank)
            db.session.commit()
            print("Ranghi nobiliari inizializzati con successo")
        else:
            print("I ranghi nobiliari esistono già")
            
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'inizializzazione dei ranghi: {str(e)}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_noble_ranks()
