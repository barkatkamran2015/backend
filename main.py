# main.py
from flask import Flask
from flask_cors import CORS
from app.blueprints.api import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all origins
    app.register_blueprint(api_bp, url_prefix='/api')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
