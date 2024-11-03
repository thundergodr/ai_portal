import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

class Config:
    # Secure the application; this should ideally be set in the .env file
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key_here')

    # Configure database; fall back on local SQLite if not set in .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/ai_portal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance

    # Enable debugging if specified in .env; defaults to False for safety in production
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

    # Future additions could include:
    # MAIL_SERVER, CACHE_TYPE, etc., as needed for your application.
