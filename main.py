
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
        ports = [8080, 8081, 8082]  # Multiple port options
        for port in ports:
            try:
                print(f"Starting server on port {port}...")
                app.run(host='0.0.0.0', port=port, debug=True)
                break
            except OSError as e:
                print(f"Port {port} is in use, trying next port...")
                if port == ports[-1]:
                    print("No available ports found. Please free up a port and try again.")
                    exit(1)
