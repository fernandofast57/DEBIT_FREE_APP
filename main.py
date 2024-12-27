import os
from config import Config  # Importa direttamente il Config dalla radice del progetto
from app import create_app

app = create_app(Config)  # Passa la classe di configurazione qui

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))  # Esegui l'app su tutte le interfacce