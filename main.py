
import os
from flask import Flask
from app import create_app
from config import Config

app = create_app(Config())

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
