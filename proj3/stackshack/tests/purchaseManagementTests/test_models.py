from decimal import Decimal
from datetime import datetime
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from database.db import db


class TestOrderModel:
    """Test cases for the Order model."""

    def test_create_order(self, app, test_user):
        """Test creating a new order."""
        with app.app_context():
            order = Order(
                user_id=test_user, total_price=Decimal("10.50"), status="Pending"
            )
            db.session.add(order)
            db.session.commit()

            assert order.id is not None
            assert order.user_id == test_user
            assert order.total_price == Decimal("10.50")
            assert order.status == "Pending"
            assert order.ordered_at is not None
            assert isinstance(order.ordered_at, datetime)

    def test_order_default_status(self, app, test_user):
        """Test that order status defaults to 'Pending'."""
        with app.app_context():
            order = Order(user_id=test_user, total_price=Decimal("5.00"))
            db.session.add(order)
            db.session.commit()

            assert order.status == "Pending"

    def test_order_to_dict(self, app, sample_order, test_user):
        """Test order to_dict serialization."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order_dict = order.to_dict()

            assert order_dict["id"] == sample_order
            assert order_dict["user_id"] == test_user
            assert order_dict["total_price"] == 6.50
            assert order_dict["status"] == "Pending"
            assert "ordered_at" in order_dict
            assert "items" in order_dict
            assert isinstance(order_dict["items"], list)
            assert len(order_dict["items"]) == 2

    def test_order_relationship_with_items(self, app, sample_order):
        """Test order relationship with order items."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            items = order.items.all()

            assert len(items) == 2
            assert all(isinstance(item, OrderItem) for item in items)
            assert all(item.order_id == sample_order for item in items)

    def test_order_relationship_with_user(self, app, sample_order, test_user):
        """Test order relationship with user."""
        with app.app_context():
            order = db.session.get(Order, sample_order)

            assert order.user is not None
            assert order.user.id == test_user
            assert order in order.user.orders.all()

    def test_order_with_zero_price(self, app, test_user):
        """Test creating an order with zero price."""
        with app.app_context():
            order = Order(
                user_id=test_user, total_price=Decimal("0.00"), status="Pending"
            )
            db.session.add(order)
            db.session.commit()

            assert order.total_price == Decimal("0.00")

    def test_order_status_update(self, app, sample_order):
        """Test updating order status."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order.status = "Completed"
            db.session.commit()

            updated_order = db.session.get(Order, sample_order)
            assert updated_order.status == "Completed"

    def test_order_multiple_status_values(self, app, test_user):
        """Test order with different status values."""
        with app.app_context():
            statuses = ["Pending", "Completed", "Cancelled", "Processing"]

            for status in statuses:
                order = Order(
                    user_id=test_user, total_price=Decimal("5.00"), status=status
                )
                db.session.add(order)
                db.session.commit()

                assert order.status == status
                db.session.delete(order)
                db.session.commit()


class TestOrderItemModel:
    """Test cases for the OrderItem model."""

    def test_create_order_item(self, app, sample_order, sample_menu_items):
        """Test creating a new order item."""
        with app.app_context():
            menu_item = db.session.get(MenuItem, sample_menu_items[2])

            order_item = OrderItem(
                order_id=sample_order,
                menu_item_id=menu_item.id,
                name=menu_item.name,
                price=menu_item.price,
                quantity=2,
            )
            db.session.add(order_item)
            db.session.commit()

            assert order_item.id is not None
            assert order_item.order_id == sample_order
            assert order_item.menu_item_id == menu_item.id
            assert order_item.name == menu_item.name
            assert order_item.price == menu_item.price
            assert order_item.quantity == 2

    def test_order_item_without_menu_item_id(self, app, sample_order):
        """Test creating order item without menu_item_id (custom item)."""
        with app.app_context():
            order_item = OrderItem(
                order_id=sample_order,
                menu_item_id=None,
                name="Custom Item",
                price=Decimal("5.00"),
                quantity=1,
            )
            db.session.add(order_item)
            db.session.commit()

            assert order_item.id is not None
            assert order_item.menu_item_id is None
            assert order_item.name == "Custom Item"

    def test_order_item_to_dict(self, app, sample_order):
        """Test order item to_dict serialization."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order_item = order.items.first()
            item_dict = order_item.to_dict()

            assert "id" in item_dict
            assert "menu_item_id" in item_dict
            assert "name" in item_dict
            assert "price" in item_dict
            assert "quantity" in item_dict
            assert isinstance(item_dict["price"], float)
            assert isinstance(item_dict["quantity"], int)

    def test_order_item_relationship_with_order(self, app, sample_order):
        """Test order item relationship with order."""
        with app.app_context():
            order = db.session.get(Order, sample_order)
            order_item = order.items.first()

            assert order_item.order is not None
            assert order_item.order.id == sample_order

    def test_multiple_quantities(self, app, sample_order, sample_menu_items):
        """Test order item with various quantities."""
        with app.app_context():
            menu_item = db.session.get(MenuItem, sample_menu_items[3])

            for qty in [1, 5, 10, 100]:
                order_item = OrderItem(
                    order_id=sample_order,
                    menu_item_id=menu_item.id,
                    name=menu_item.name,
                    price=menu_item.price,
                    quantity=qty,
                )
                db.session.add(order_item)
                db.session.commit()

                assert order_item.quantity == qty
                db.session.delete(order_item)
                db.session.commit()

    def test_order_item_price_precision(self, app, sample_order):
        """Test order item price with decimal precision."""
        with app.app_context():
            order_item = OrderItem(
                order_id=sample_order,
                menu_item_id=None,
                name="Precise Item",
                price=Decimal("3.99"),
                quantity=3,
            )
            db.session.add(order_item)
            db.session.commit()

            retrieved_item = db.session.get(OrderItem, order_item.id)
            assert retrieved_item.price == Decimal("3.99")

            # Test to_dict conversion
            item_dict = retrieved_item.to_dict()
            assert item_dict["price"] == 3.99

    def test_order_item_cascade_delete(self, app, test_user, sample_menu_items):
        """Test that order items are deleted when order is deleted (cascade)."""
        with app.app_context():
            # Create a new order
            order = Order(
                user_id=test_user, total_price=Decimal("5.00"), status="Pending"
            )
            db.session.add(order)
            db.session.flush()

            # Add items
            menu_item = db.session.get(MenuItem, sample_menu_items[0])
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                name=menu_item.name,
                price=menu_item.price,
                quantity=1,
            )
            db.session.add(order_item)
            db.session.commit()

            order_id = order.id
            order_item_id = order_item.id

            # Delete the order
            db.session.delete(order)
            db.session.commit()

            # Check that order is deleted
            deleted_order = db.session.get(Order, order_id)
            assert deleted_order is None

            # Check if order item is also deleted (cascade='all, delete-orphan')
            deleted_item = db.session.get(OrderItem, order_item_id)
            assert deleted_item is None  # Should be deleted due to cascade
