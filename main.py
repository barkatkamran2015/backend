from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({'message': 'API is live and operational'}), 200

    # Additional configurations and routes
    return app

app = create_app()
