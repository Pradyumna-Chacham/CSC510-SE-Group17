# A script to create database tables for the StackShack application.
from app import create_app
from database.db import db


def create_tables():
    """Creates all database tables."""
    app = create_app(config_name="development")

    with app.app_context():
        print("Creating database tables...")
        # db.create_all() will create all tables that inherit from db.Model
        db.create_all()
        print("✅ Database tables created successfully!")


create_tables()
