from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager

app = Flask(__name__)  # Initialize the Flask application
app.config.from_object(Config)  # Load configuration from Config class
print(app.config['SQLALCHEMY_DATABASE_URI'])  # Print the database URI for debugging
db = SQLAlchemy(app)  # Initialize SQLAlchemy
migrate = Migrate(app, db)  # Initialize Flask-Migrate
login_manager = LoginManager(app)  # Initialize Flask-Login
login_manager.login_view = 'login'  # Set the login view for Flask-Login

from app.models import User  # Import User model after db initialization

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load the user from the database

from app import routes, models  # Import routes and models at the end