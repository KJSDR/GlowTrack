"""Flask configuration."""
import os

class Config:
    """Set Flask configuration from environment variables."""

    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database Config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///glowtrack.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for product images
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    
    # Make sure the upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)