"""
This module contains the setup logic for the API and the database it uses
and automates it by:
- installing required dependencies
- creating the database
- populating the database
- and starting the flask application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt."""
    req_file = os.path.join(os.path.dirname(__file__), "Database_folder", "requirements.txt")
    print("=== Installing requirements ===")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask-restful"])
    print("Requirements installed successfully.\n")

def create_and_populate_db():
    """Create database tables and populate with sample data."""
    app_dir = os.path.dirname(__file__)
    db_dir = os.path.join(os.path.dirname(__file__), "Database_folder")
    sys.path.insert(0, app_dir)

    from Beatify.models import db, app

    print("Creating database...")
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("Database created successfully.\n")

    print("=== Populating database ===")
    env = os.environ.copy()
    env["PYTHONPATH"] = app_dir + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.check_call([sys.executable, os.path.join(db_dir, "populate_DB.py")], env=env, cwd=app_dir)
    print("Database populated successfully.\n")

def start_app():
    """Start the Flask application."""
    app_dir = os.path.dirname(__file__)
    print("=== Starting application ===")
    subprocess.call([sys.executable, "-m", "Beatify.api"], cwd=app_dir)

if __name__ == "__main__":
    install_requirements()
    create_and_populate_db()
    start_app()
