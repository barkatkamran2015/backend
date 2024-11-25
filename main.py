from flask import Flask, jsonify
from app.blueprints.api import api_bp

def create_app():
    app = Flask(__name__)

    # Health check route
    @app.route('/', methods=['GET', 'POST'])
    def home():
        return jsonify({'message': 'API is live and operational'}), 200

    # Register the API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

app = create_app()
