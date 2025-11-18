import pytest
import sys
import os
from decimal import Decimal

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
def test_customer_user(app):
    """Create a test customer user."""
    with app.app_context():
        user = User(username="customer1")
        user.set_password("password123")
        user.role = "customer"
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def test_staff_user(app):
    """Create a test staff user."""
    with app.app_context():
        user = User(username="staff1")
        user.set_password("staffpass123")
        user.role = "staff"
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def test_admin_user(app):
    """Create a test admin user."""
    with app.app_context():
        user = User(username="admin1")
        user.set_password("adminpass123")
        user.role = "admin"
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope="function")
def sample_menu_items(app):
    """Create sample menu items for testing."""
    with app.app_context():
        items = [
            MenuItem(
                name="Burger",
                description="Tasty burger",
                price=Decimal("5.50"),
                category="burger",
                is_available=True,
                is_healthy_choice=False,
                image_url="/static/images/burger.png",
            ),
            MenuItem(
                name="Fries",
                description="Crispy fries",
                price=Decimal("2.50"),
                category="sides",
                is_available=True,
                is_healthy_choice=False,
                image_url="/static/images/fries.png",
            ),
        ]

        for item in items:
            db.session.add(item)
        db.session.commit()

        return [item.id for item in items]


@pytest.fixture(scope="function")
def pending_order(app, test_customer_user, sample_menu_items):
    """Create a pending order."""
    with app.app_context():
        order = Order(
            user_id=test_customer_user, total_price=Decimal("8.00"), status="Pending"
        )
        db.session.add(order)
        db.session.flush()

        item = db.session.get(MenuItem, sample_menu_items[0])
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.id,
            name=item.name,
            price=item.price,
            quantity=1,
        )
        db.session.add(order_item)
        db.session.commit()

        return order.id


@pytest.fixture(scope="function")
def preparing_order(app, test_customer_user, sample_menu_items):
    """Create a preparing order."""
    with app.app_context():
        order = Order(
            user_id=test_customer_user, total_price=Decimal("8.00"), status="Preparing"
        )
        db.session.add(order)
        db.session.flush()

        item = db.session.get(MenuItem, sample_menu_items[0])
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.id,
            name=item.name,
            price=item.price,
            quantity=1,
        )
        db.session.add(order_item)
        db.session.commit()

        return order.id


@pytest.fixture(scope="function")
def ready_order(app, test_customer_user, sample_menu_items):
    """Create a ready for pickup order."""
    with app.app_context():
        order = Order(
            user_id=test_customer_user,
            total_price=Decimal("8.00"),
            status="Ready for Pickup",
        )
        db.session.add(order)
        db.session.flush()

        item = db.session.get(MenuItem, sample_menu_items[0])
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.id,
            name=item.name,
            price=item.price,
            quantity=1,
        )
        db.session.add(order_item)
        db.session.commit()

        return order.id


@pytest.fixture(scope="function")
def delivered_order(app, test_customer_user, sample_menu_items):
    """Create a delivered order."""
    with app.app_context():
        order = Order(
            user_id=test_customer_user, total_price=Decimal("8.00"), status="Delivered"
        )
        db.session.add(order)
        db.session.flush()

        item = db.session.get(MenuItem, sample_menu_items[0])
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.id,
            name=item.name,
            price=item.price,
            quantity=1,
        )
        db.session.add(order_item)
        db.session.commit()

        return order.id


@pytest.fixture(scope="function")
def cancelled_order(app, test_customer_user, sample_menu_items):
    """Create a cancelled order."""
    with app.app_context():
        order = Order(
            user_id=test_customer_user, total_price=Decimal("8.00"), status="Cancelled"
        )
        db.session.add(order)
        db.session.flush()

        item = db.session.get(MenuItem, sample_menu_items[0])
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.id,
            name=item.name,
            price=item.price,
            quantity=1,
        )
        db.session.add(order_item)
        db.session.commit()

        return order.id


@pytest.fixture(scope="function")
def multiple_orders_various_statuses(app, test_customer_user, sample_menu_items):
    """Create multiple orders with various statuses."""
    with app.app_context():
        statuses = ["Pending", "Preparing", "Ready for Pickup", "Delivered"]
        order_ids = []

        for status in statuses:
            order = Order(
                user_id=test_customer_user, total_price=Decimal("8.00"), status=status
            )
            db.session.add(order)
            db.session.flush()

            item = db.session.get(MenuItem, sample_menu_items[0])
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                name=item.name,
                price=item.price,
                quantity=1,
            )
            db.session.add(order_item)
            order_ids.append(order.id)

        db.session.commit()
        return order_ids
