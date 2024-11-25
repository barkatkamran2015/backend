from flask import Flask, jsonify
from flask_cors import CORS
from yourapp.blueprints.api import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({'message': 'API is running'}), 200

    return app
