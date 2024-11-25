from flask import Flask
from flask_cors import CORS
from app.blueprints.api import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api_bp, url_prefix='/api')
    return app

app = create_app()  # Create the app instance

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
