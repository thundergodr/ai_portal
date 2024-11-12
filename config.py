import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///C:\\Users\\Troy\\ai_portal\\instance\\ai_portal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
