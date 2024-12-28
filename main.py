
import os
from flask import Flask
from flask_cors import CORS
from app import create_app
from config import Config

app = create_app(Config())
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    with app.app_context():
        port = int(os.getenv('PORT', 5000))
        app.run(host='0.0.0.0', port=3000, debug=True)
