from flask import Flask
from app.blueprints.api import api_bp  # Import the blueprint

def create_app():
    app = Flask(__name__)
    
    # Health check route (optional but useful for Render's health checks)
    @app.route('/', methods=['GET', 'POST'])
    def home():
        return jsonify({'message': 'API is live and operational'}), 200

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

app = create_app()
