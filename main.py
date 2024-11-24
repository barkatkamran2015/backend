def create_app():
    app = Flask(__name__)

    # Register the API Blueprint with a prefix
    app.register_blueprint(api_bp, url_prefix='/api')

    # Add a root route
    @app.route("/")
    def home():
        return "Backend is live!", 200

    return app
