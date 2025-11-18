from app import create_app
from database.db import db
from models.user import User

app = create_app()
with app.app_context():
    # Create admin user
    admin = User(username="admin", role="admin")
    # IMPORTANT: Use a secure, password. (One time only to create an admin)
    admin.set_password(
        "admin"
    )  # Put a strong password for creating an admin user (rolas=admin)
    # with the required password
    db.session.add(admin)
    db.session.commit()
    print("Admin user created")
