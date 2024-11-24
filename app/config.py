import os
from dotenv import load_dotenv

# Load environment variables
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

# Flask-specific configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')  # Default if not provided
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'       # Enable/disable debug mode
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')  # Default SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False                      # Recommended False for Flask-SQLAlchemy

# Veryfi configuration
veryfi_config = {
    "client_id": os.getenv('VF_CLIENT_ID'),
    "client_secret": os.getenv('VF_CLIENT_SECRET'),
    "username": os.getenv('VF_USERNAME'),
    "api_key": os.getenv('VF_API_KEY'),
    "api_url": os.getenv('VF_API_URL')
}

# OpenAI configuration
openai_config = {
    "api_key": os.getenv('OPENAI_API_KEY')
}
