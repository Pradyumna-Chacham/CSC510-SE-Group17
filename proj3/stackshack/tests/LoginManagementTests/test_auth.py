# stackshack/test_auth.py
from urllib.parse import urlparse
from models.user import User
from controllers.auth_controller import AuthController

# --- ANONYMOUS ACCESS & REDIRECTS ---


def test_homepage_access_nominal(client):
    """Anonymous user can access the homepage."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 200
    assert b"Welcome to Stack Shack" in response.data


def test_login_page_access_nominal(client):
    """Anonymous user can access the login page."""
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 200
    assert b"Account Login" in response.data


def test_register_page_access_nominal(client):
    """Anonymous user can access the registration page."""
    response = client.get("/auth/register", follow_redirects=False)
    assert response.status_code == 200
    assert b"Register New Account" in response.data


def test_protected_route_redirect_security(client):
    """Anonymous user is redirected to login for a protected route like dashboard."""
    response = client.get("/auth/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert urlparse(response.headers["Location"]).path == "/auth/login"


# --- USER REGISTRATION ---


def test_nominal_customer_registration(client, db_session):
    """T5: Nominal - New customer registration succeeds and redirects to login."""
    new_username = "newcust01"
    response = client.post(
        "/auth/register",
        data=dict(username=new_username, password="testpassword"),
        follow_redirects=True,
    )

    user = User.get_by_username(new_username)

    assert response.status_code == 200
    assert b"Customer user created successfully." in response.data
    assert user is not None
    assert user.role == "customer"


def test_register_duplicate_username_off_nominal(client):
    """Fails to register with duplicate username (test_admin)."""
    response = client.post(
        "/auth/register",
        data=dict(username="test_admin", password="anypassword"),
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Username already exists" in response.data


def test_register_empty_username_off_nominal(client):
    """Fails to register with empty username."""
    response = client.post(
        "/auth/register",
        data=dict(username="", password="password"),
        follow_redirects=True,
    )

    assert b"Username and password required" in response.data


def test_register_empty_password_off_nominal(client):
    """Fails to register with empty password."""
    response = client.post(
        "/auth/register",
        data=dict(username="nopass", password=""),
        follow_redirects=True,
    )

    assert b"Username and password required" in response.data


def test_register_role_bypass_security_anon(client, db_session):
    """Security - Anonymous attempt to set role='admin' defaults to 'customer'."""
    hacker_username = "hacker01"
    client.post(
        "/auth/register",
        data=dict(username=hacker_username, password="hackerpass", role="admin"),
        follow_redirects=True,
    )

    user = User.get_by_username(hacker_username)
    assert user.role == "customer"


# --- LOGIN AND LOGOUT ---


def test_nominal_login_admin(client, login):
    """Admin logs in successfully and sees dashboard."""
    response = login("test_admin", "adminpass")
    assert response.status_code == 200
    assert b"Welcome, test_admin!" in response.data


def test_nominal_login_customer(client, login):
    """Customer logs in successfully and sees dashboard."""
    response = login("test_customer", "customerpass")
    assert response.status_code == 200
    assert b"Welcome, test_customer!" in response.data


def test_login_bad_password_off_nominal(client, login):
    """Login fails with correct username, wrong password."""
    response = login("test_customer", "wrongpassword")
    assert b"Incorrect username or password." in response.data


def test_login_nonexistent_user_off_nominal(client, login):
    """Login fails with non-existent username."""
    response = login("ghostuser", "anypass")
    assert b"Incorrect username or password." in response.data


def test_login_when_authenticated_off_nominal(client, login):
    """Authenticated user accessing /auth/login is redirected to dashboard."""
    login("test_customer", "customerpass")
    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 302
    assert urlparse(response.headers["Location"]).path == "/auth/dashboard"


def test_nominal_logout(client, login):
    """User logs out successfully and is redirected to login."""
    login("test_customer", "customerpass")
    response = client.get("/auth/logout", follow_redirects=True)
    assert b"Logged out successfully." in response.data
    assert b"Account Login" in response.data


# --- RBAC ACCESS ---


def test_dashboard_content_admin(client, login):
    """Admin dashboard shows correct role and admin links."""
    response = login("test_admin", "adminpass")
    assert b"Your Role: <strong>ADMIN</strong>" in response.data
    assert b"Create Staff/Admin" in response.data
    assert b"Manage Users" in response.data


def test_dashboard_content_staff(client, login):
    """Staff dashboard shows correct role and staff links (Manage Menu)."""
    response = login("test_staff", "staffpass")
    assert b"Your Role: <strong>STAFF</strong>" in response.data
    assert b"Staff Tools" in response.data
    assert b"Manage Users" not in response.data


def test_dashboard_content_customer(client, login):
    """Customer dashboard shows correct role and no tools links."""
    response = login("test_customer", "customerpass")
    assert b"Your Role: <strong>CUSTOMER</strong>" in response.data
    assert b"Admin Tools" not in response.data
    assert b"Staff Tools" not in response.data


def test_customer_cannot_access_admin_manage_security(client, login):
    """Security - Customer access to /auth/admin/manage-users redirects to dashboard."""
    login("test_customer", "customerpass")
    response = client.get("/auth/admin/manage-users", follow_redirects=False)
    assert response.status_code == 302
    assert urlparse(response.headers["Location"]).path == "/auth/dashboard"


def test_staff_cannot_access_admin_manage_security(client, login):
    """Security - Staff access to /auth/admin/manage-users redirects to dashboard."""
    login("test_staff", "staffpass")
    response = client.get("/auth/admin/manage-users", follow_redirects=False)
    assert response.status_code == 302
    assert urlparse(response.headers["Location"]).path == "/auth/dashboard"


# --- ADMIN USER MANAGEMENT (ROUTES) ---


def test_admin_can_access_manage_users_page_nominal(client, login):
    """Admin can access the /auth/admin/manage-users page."""
    login("test_admin", "adminpass")
    response = client.get("/auth/admin/manage-users", follow_redirects=True)
    assert response.status_code == 200
    assert b"Manage Users" in response.data
    assert b"test_customer" in response.data


def test_admin_create_admin_user_nominal(client, login, db_session):
    """Admin successfully creates a new admin user via admin route."""
    login("test_admin", "adminpass")
    new_admin_username = "new_admin_01"
    response = client.post(
        "/auth/admin/create-user",
        data=dict(username=new_admin_username, password="password", role="admin"),
        follow_redirects=True,
    )

    user = User.get_by_username(new_admin_username)
    assert b"Admin user created successfully." in response.data
    assert user.role == "admin"


def test_admin_update_customer_to_staff_nominal(client, login, db_session):
    """Admin successfully updates a customer role to staff via POST."""
    login("test_admin", "adminpass")
    customer = User.query.filter_by(username="test_customer").first()

    response = client.post(
        "/auth/admin/manage-users",
        data=dict(user_id=customer.id, role="staff", update_role="Update Role"),
        follow_redirects=True,
    )

    db_session.refresh(customer)
    assert b"Role updated successfully" in response.data
    assert customer.role == "staff"


def test_admin_delete_staff_user_nominal(client, login, db_session):
    """Admin successfully deletes a staff user."""
    login("test_admin", "adminpass")
    user_to_delete = User(username="todelete_route", role="staff")
    user_to_delete.set_password("pass")
    db_session.add(user_to_delete)
    db_session.commit()
    user_id = user_to_delete.id

    response = client.post(
        "/auth/admin/manage-users",
        data=dict(user_id=user_id, delete_user="Delete"),
        follow_redirects=True,
    )

    deleted_user = db_session.get(User, user_id)
    assert b"User deleted successfully" in response.data
    assert deleted_user is None


def test_admin_update_nonexistent_user_role_off_nominal(client, login):
    """Admin attempts to update role of a non-existent user."""
    login("test_admin", "adminpass")

    response = client.post(
        "/auth/admin/manage-users",
        data=dict(user_id="99999", role="admin", update_role="Update Role"),
        follow_redirects=True,
    )

    assert b"User not found" in response.data


def test_admin_delete_nonexistent_user_off_nominal(client, login):
    """Admin attempts to delete a non-existent user."""
    login("test_admin", "adminpass")

    response = client.post(
        "/auth/admin/manage-users",
        data=dict(user_id="99999", delete_user="Delete"),
        follow_redirects=True,
    )

    assert b"User not found" in response.data


def test_admin_cannot_delete_self_ui_security(client, login):
    """Security - Verify Admin user cannot delete their own account from the UI."""
    login("test_admin", "adminpass")
    response = client.get("/auth/admin/manage-users", follow_redirects=True)

    assert b"(You)" in response.data


# --- CONTROLLER LOGIC (DIRECT TESTING) ---


def test_controller_register_admin_unauthorized_security(db_session, app):
    """Security - Directly test that AuthController blocks non-admin role elevation."""

    with app.test_request_context():
        # current_user resolves to AnonymousUserMixin in this context
        success, msg, user = AuthController.register_user(
            username="anon_hacker_ctrl", password="p", role="admin"
        )

    assert success is False
    assert msg == "Unauthorized: Only admins can assign elevated roles."


def test_controller_login_user_not_found_off_nominal(db_session):
    """Directly test AuthController failure when user is not found."""
    success, msg, user = AuthController.login_user_account(
        username="i_dont_exist", password="any"
    )

    assert success is False
    assert msg == "Incorrect username or password."
    assert user is None


def test_controller_update_role_nonexistent_off_nominal(db_session):
    """Directly test AuthController update role failure with bad ID."""
    success, msg = AuthController.update_user_role(user_id=99999, new_role="admin")

    assert success is False
    assert msg == "User not found"


def test_controller_delete_user_nominal(db_session):
    """Directly test AuthController's delete logic."""
    user = User(username="todelete_ctrl_2", role="customer")
    user.set_password("pass")
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    success, msg = AuthController.delete_user(user_id)

    assert success is True
    assert msg == "User deleted successfully"

    deleted_user = db_session.get(User, user_id)
    assert deleted_user is None
