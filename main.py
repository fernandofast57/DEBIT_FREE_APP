
import os
from app import create_app
from app.utils.advanced_config import initialize_system

# Initialize system with advanced configuration
config = initialize_system()
logger = config.logger

app = create_app()

if __name__ == '__main__':
    logger.info('Gold Investment startup')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
