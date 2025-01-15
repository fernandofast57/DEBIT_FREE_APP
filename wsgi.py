# wsgi.py
from app import create_app
from config import ProductionConfig, DevelopmentConfig, TestingConfig
import os

# Scegli la configurazione in base all'ambiente
env = os.environ.get('FLASK_ENV', 'production')
config_map = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}

app = create_app(config_map[env])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
