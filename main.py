
import os
from flask import Flask
from flask_cors import CORS
from app import create_app
from app.config.constants import Config

app = create_app(Config())
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    with app.app_context():
        port = int(os.getenv('PORT', 8080))
        try:
            app.run(host='0.0.0.0', port=port, debug=True)
        except OSError as e:
            print(f"Errore nell'avvio del server: {e}")
            print("Provo una porta alternativa...")
            app.run(host='0.0.0.0', port=8081, debug=True)
