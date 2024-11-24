from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Allow cross-origin requests from your React Native app
    app.register_blueprint(api_bp, url_prefix='/api')
    return app
