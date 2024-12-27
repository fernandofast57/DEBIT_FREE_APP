
import os
from config import Config
from app import create_app

app = create_app(Config())

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
