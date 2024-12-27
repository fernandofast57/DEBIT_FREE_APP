import os
import os
from flask import Flask, jsonify
from app import create_app
from config import Config

app = create_app(Config)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)