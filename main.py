from flask import Flask, jsonify
from app.blueprints.api import api_bp  # Import the blueprint

def create_app():
    app = Flask(__name__)
    
    # Root route for health check
    @app.route('/', methods=['GET', 'POST'])
    def home():
        return jsonify({'message': 'API is live and operational'}), 200

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')  # Register the API blueprint

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': str(error)}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500

    return app

app = create_app()
