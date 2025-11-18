import pytest
from app import create_app
from database.db import db
from models.user import User
from models.menu_item import MenuItem


@pytest.fixture(scope="function")
def app():
    """Create application for testing"""
    app = create_app("testing")  # <--- THE ONLY CHANGE YOU NEED

    # All the other config is now handled by TestingConfig

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    """Create admin user for testing"""
    admin = User(username="testadmin", role="admin")
    admin.set_password("testpass")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def staff_user(app):
    """Create staff user for testing"""
    staff = User(username="teststaff", role="staff")
    staff.set_password("testpass")
    db.session.add(staff)
    db.session.commit()
    return staff


@pytest.fixture
def customer_user(app):
    """Create customer user for testing"""
    customer = User(username="testcustomer", role="customer")
    customer.set_password("testpass")
    db.session.add(customer)
    db.session.commit()
    return customer


@pytest.fixture
def sample_menu_item(app):
    """Create a sample menu item"""
    item = MenuItem(
        name="Test Burger",
        category="patty",
        description="Test description",
        price=5.99,
        calories=300,
        protein=25,
        is_available=True,
        is_healthy_choice=False,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture
def multiple_menu_items(app):
    """Create multiple menu items for testing"""
    items = [
        MenuItem(
            name="Sesame Bun",
            category="bun",
            price=1.50,
            calories=180,
            protein=5,
            is_available=True,
        ),
        MenuItem(
            name="Beef Patty",
            category="patty",
            price=3.50,
            calories=250,
            protein=20,
            is_available=True,
        ),
        MenuItem(
            name="Turkey Patty",
            category="patty",
            price=3.00,
            calories=180,
            protein=22,
            is_available=False,
        ),
        MenuItem(
            name="Lettuce",
            category="topping",
            price=0.50,
            calories=5,
            protein=0,
            is_available=True,
            is_healthy_choice=True,
        ),
        MenuItem(
            name="Ketchup",
            category="sauce",
            price=0.25,
            calories=15,
            protein=0,
            is_available=True,
        ),
    ]
    for item in items:
        db.session.add(item)
    db.session.commit()
    return items
