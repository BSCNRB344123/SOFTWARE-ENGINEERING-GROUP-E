import os

class Config(object):
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'  # Replace with a strong, randomly generated key
    # Database URI for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Use SQLite for now
    # Disable SQLAlchemy event notifications for performance improvement
    SQLALCHEMY_TRACK_MODIFICATIONS = False
