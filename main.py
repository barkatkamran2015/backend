from flask import Flask
from app.blueprints.api import api_bp  # Import your blueprint

def create_app():
    app = Flask(__name__)

    # Register the API blueprint with the /api prefix
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

app = create_app()
