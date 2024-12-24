
from app import create_app
from config import Config  # Assicurati di importare la tua Config

app = create_app(Config)  # Passa la classe di configurazione qui

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Usa 0.0.0.0 per l'accessibilità esterna
