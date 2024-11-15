import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///health_center.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
