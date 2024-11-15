#!/bin/bash

# Install dependencies
pip install flask flask-sqlalchemy flask-migrate flask-wtf

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run the application
export FLASK_APP=app.py
export FLASK_ENV=production
flask run
