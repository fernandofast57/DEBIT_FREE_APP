import os
from app.config import Config  # Assicurati di importare la classe Config
from app import create_app

app = create_app(Config)  # Passa la classe di configurazione qui

if __name__ == '__main__':
    app.logger.info('Starting Gold Investment Platform')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
