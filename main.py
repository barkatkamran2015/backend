from flask import Flask

def create_app():
    app = Flask(__name__)

    # Adjust imports to reflect the module structure
    from app.blueprints.api import api_bp
    from app.blueprints.web import web_bp

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp, url_prefix="/web")

    # Additional configuration
    app.config.from_object("app.config.Config")

    return app
