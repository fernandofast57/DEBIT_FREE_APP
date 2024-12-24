import os
from app.config import Config  # Assicurati che questa riga sia presente
from app import create_app
app = create_app(Config)  # Passa la classe di configurazione qui
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Aggiorna l'host
