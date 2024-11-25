from flask import Flask
from app.blueprints.api import api_bp  # Ensure this import path is correct

def create_app():
    app = Flask(__name__)
    # Configure your app here, like setting up configurations, databases, registering blueprints, etc.
    app.register_blueprint(api_bp, url_prefix='/api')
    return app

app = create_app()  # This line is crucial, it creates the 'app' object
