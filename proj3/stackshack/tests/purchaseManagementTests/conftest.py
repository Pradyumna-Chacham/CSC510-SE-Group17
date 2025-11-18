import pytest
import sys
import os
from decimal import Decimal

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import create_app
from database.db import db
from models.user import User
from models.menu_item import MenuItem
from models.order import Order, OrderItem


@pytest.fixture(scope="function")
def app():
    """Create and configure a test application instance."""
    app = create_app("testing")

    # Configure test database
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(username="testuser")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()

        user_id = user.id

        return user_id


@pytest.fixture(scope="function")
def authenticated_client(client, app, test_user):
    """Create an authenticated test client by mocking current_user."""
    with app.app_context():
        user = db.session.get(User, test_user)

        # Mock the current_user within the app context
        with client.session_transaction() as sess:
            sess["_user_id"] = str(test_user)
            sess["_fresh"] = True

        # Patch Flask-Login's current_user to return our test user
        from flask_login import login_user

        with client:
            # Make a request to set up the session
            with app.test_request_context():
                login_user(user)
            yield client


@pytest.fixture(scope="function")
def sample_menu_items(app):
    """Create sample menu items for testing."""
    with app.app_context():
        items = [
            MenuItem(
                name="Classic Bun",
                description="Soft sesame bun",
                price=Decimal("1.50"),
                category="bun",
                is_available=True,
                is_healthy_choice=True,
                image_url="/static/images/bun.png",
            ),
            MenuItem(
                name="Beef Patty",
                description="100% beef patty",
                price=Decimal("3.50"),
                category="patty",
                is_available=True,
                is_healthy_choice=False,
                image_url="/static/images/beef.png",
            ),
            MenuItem(
                name="Cheddar Cheese",
                description="Melted cheddar cheese",
                price=Decimal("1.00"),
                category="cheese",
                is_available=True,
                is_healthy_choice=False,
                image_url="/static/images/cheddar.png",
            ),
            MenuItem(
                name="Lettuce",
                description="Fresh lettuce",
                price=Decimal("0.50"),
                category="topping",
                is_available=True,
                is_healthy_choice=True,
                image_url="/static/images/lettuce.png",
            ),
            MenuItem(
                name="Ketchup",
                description="Tomato ketchup",
                price=Decimal("0.25"),
                category="sauce",
                is_available=True,
                is_healthy_choice=True,
                image_url="/static/images/ketchup.png",
            ),
            MenuItem(
                name="Unavailable Item",
                description="Not in stock",
                price=Decimal("2.00"),
                category="topping",
                is_available=False,
                is_healthy_choice=False,
                image_url="/static/images/unavailable.png",
            ),
        ]

        for item in items:
            db.session.add(item)
        db.session.commit()

        item_ids = [item.id for item in items]

        return item_ids


@pytest.fixture(scope="function")
def sample_order(app, test_user, sample_menu_items):
    """Create a sample order for testing."""
    with app.app_context():
        order = Order(user_id=test_user, total_price=Decimal("6.50"), status="Pending")
        db.session.add(order)
        db.session.flush()

        bun = db.session.get(MenuItem, sample_menu_items[0])
        patty = db.session.get(MenuItem, sample_menu_items[1])

        order_items = [
            OrderItem(
                order_id=order.id,
                menu_item_id=bun.id,
                name=bun.name,
                price=bun.price,
                quantity=1,
            ),
            OrderItem(
                order_id=order.id,
                menu_item_id=patty.id,
                name=patty.name,
                price=patty.price,
                quantity=1,
            ),
        ]

        for item in order_items:
            db.session.add(item)

        db.session.commit()

        order_id = order.id

        return order_id


@pytest.fixture(scope="function")
def multiple_orders(app, test_user, sample_menu_items):
    """Create multiple orders for testing order history."""
    with app.app_context():
        order_ids = []
        for i in range(3):
            order = Order(
                user_id=test_user,
                total_price=Decimal("5.00") * (i + 1),
                status="Pending" if i == 0 else "Completed",
            )
            db.session.add(order)
            db.session.flush()

            item = db.session.get(MenuItem, sample_menu_items[0])
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                name=item.name,
                price=item.price,
                quantity=i + 1,
            )
            db.session.add(order_item)
            order_ids.append(order.id)

        db.session.commit()
        return order_ids
