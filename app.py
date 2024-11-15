from flask import Flask
from config import Config
from models import db, migrate
from routes import patient_routes, appointment_routes, doctor_routes, auth_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(patient_routes.bp)
    app.register_blueprint(appointment_routes.bp)
    app.register_blueprint(doctor_routes.bp)
    app.register_blueprint(auth_routes.bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
