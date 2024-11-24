from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Register blueprints
    from app.blueprints.api import api_bp
    from app.blueprints.web import web_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp, url_prefix="/web")

    return app
