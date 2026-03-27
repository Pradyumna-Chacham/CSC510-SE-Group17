from models.user import User
from database.db import db
from flask_login import login_user, logout_user, current_user


class AuthController:
    """
    Controller class for handling all user authentication and management logic,
    including registration, login, logout, and CRUD operations for users and roles.
    """

    @staticmethod
    def register_user(username, password, role="customer"):
        """
        Registers a new user account. Enforces that only authenticated admins
        can assign 'admin' or 'staff' roles.

        Args:
            username (str): The username for the new account.
            password (str): The plaintext password to be hashed and stored.
            role (str, optional): The user's role. Defaults to 'customer'.

        Returns:
            tuple: (success (bool), message (str), user (User or None))
        """
        if User.get_by_username(username):
            return False, "Username already exists", None

        if not username or not password:
            return False, "Username and password required", None

        # Only admins can assign elevated roles
        if role in ["admin", "staff"]:
            if not current_user.is_authenticated or current_user.role != "admin":
                return (
                    False,
                    "Unauthorized: Only admins can assign elevated roles.",
                    None,
                )

        try:
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return True, f"{user.role.capitalize()} user created successfully.", user
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}", None

    @staticmethod
    def login_user_account(username, password):
        """
        Authenticates a user by checking credentials and logs them into the session.

        Args:
            username (str): The username provided by the user.
            password (str): The plaintext password provided by the user.

        Returns:
            tuple: (success (bool), message (str), user (User or None))
        """
        user = User.get_by_username(username)
        if not user or not user.check_password(password):
            return False, "Incorrect username or password.", None

        login_user(user)

        return True, "Login successful", user

    @staticmethod
    def logout_user_account():
        """
        Logs the current user out of the session.

        Returns:
            tuple: (success (bool), message (str))
        """
        logout_user()
        return True, "Logged out successfully."

    @staticmethod
    def get_all_users():
        """
        Retrieves all users from the database.

        Returns:
            list: A list of all User objects.
        """
        return User.query.all()

    @staticmethod
    def update_user_role(user_id, new_role):
        """
        Updates the role of a specified user.
        """
        user = db.session.get(User, int(user_id))
        if not user:
            return False, "User not found"
        user.role = new_role
        db.session.commit()
        return True, "Role updated successfully"

    @staticmethod
    def delete_user(user_id):
        """
        Deletes a user account from the database.
        """
        user = db.session.get(User, int(user_id))
        if not user:
            return False, "User not found"
        db.session.delete(user)
        db.session.commit()
        return True, "User deleted successfully"
