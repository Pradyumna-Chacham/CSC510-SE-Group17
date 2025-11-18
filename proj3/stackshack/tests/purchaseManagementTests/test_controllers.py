from decimal import Decimal
from controllers.order_controller import OrderController
from models.order import Order
from database.db import db


class TestOrderController:
    """Test cases for OrderController methods."""

    def test_get_user_orders_success(self, app, test_user, sample_order):
        """Test retrieving orders for a user successfully."""
        with app.app_context():
            success, message, orders = OrderController.get_user_orders(test_user)

            assert success is True
            assert message == "Orders retrieved successfully"
            assert orders is not None
            assert len(orders) >= 1
            assert all(isinstance(order, Order) for order in orders)
            assert all(order.user_id == test_user for order in orders)

    def test_get_user_orders_no_orders(self, app, test_user):
        """Test retrieving orders when user has no orders."""
        with app.app_context():
            success, message, orders = OrderController.get_user_orders(test_user)

            assert success is True
            assert message == "Orders retrieved successfully"
            assert orders is not None
            assert len(orders) == 0

    def test_get_user_orders_multiple(self, app, test_user, multiple_orders):
        """Test retrieving multiple orders for a user."""
        with app.app_context():
            success, message, orders = OrderController.get_user_orders(test_user)

            assert success is True
            assert len(orders) == 3
            # Check they are ordered by date descending (most recent first)
            order_dates = [order.ordered_at for order in orders]
            assert order_dates == sorted(order_dates, reverse=True)

    def test_get_user_orders_different_users(self, app, test_user, sample_order):
        """Test that orders are filtered by user_id correctly."""
        with app.app_context():
            # Create another user
            from models.user import User

            another_user = User(username="anotheruser")
            another_user.set_password("password123")
            db.session.add(another_user)
            db.session.commit()

            # Get orders for the other user (should be empty)
            success, message, orders = OrderController.get_user_orders(another_user.id)

            assert success is True
            assert len(orders) == 0

    def test_create_new_order_success(self, app, test_user, sample_menu_items):
        """Test creating a new order successfully."""
        with app.app_context():
            item_data = [
                (sample_menu_items[0], "1.50", 1, "Classic Bun"),
                (sample_menu_items[1], "3.50", 2, "Beef Patty"),
                (sample_menu_items[2], "1.00", 1, "Cheddar Cheese"),
            ]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            assert "placed successfully" in message
            assert order is not None
            assert order.user_id == test_user
            assert order.total_price == Decimal("9.50")  # 1.50 + (3.50*2) + 1.00
            assert order.status == "Pending"

            # Verify order items were created
            order_items = order.items.all()
            assert len(order_items) == 3

    def test_create_new_order_empty_items(self, app, test_user):
        """Test creating an order with no items."""
        with app.app_context():
            success, message, order = OrderController.create_new_order(test_user, [])

            assert success is False
            assert message == "Order cannot be empty."
            assert order is None

    def test_create_new_order_single_item(self, app, test_user, sample_menu_items):
        """Test creating an order with a single item."""
        with app.app_context():
            item_data = [(sample_menu_items[1], "3.50", 1, "Beef Patty")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            assert order.total_price == Decimal("3.50")
            assert len(order.items.all()) == 1

    def test_create_new_order_zero_quantity(self, app, test_user, sample_menu_items):
        """Test creating an order with zero quantity items (should be skipped)."""
        with app.app_context():
            item_data = [
                (sample_menu_items[0], "1.50", 0, "Classic Bun"),
                (sample_menu_items[1], "3.50", 2, "Beef Patty"),
            ]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            # Only the second item should be added (qty > 0)
            assert order.total_price == Decimal("7.00")  # 3.50 * 2
            assert len(order.items.all()) == 1

    def test_create_new_order_negative_quantity(
        self, app, test_user, sample_menu_items
    ):
        """Test creating an order with negative quantity (should be skipped)."""
        with app.app_context():
            item_data = [
                (sample_menu_items[0], "1.50", -1, "Classic Bun"),
                (sample_menu_items[1], "3.50", 1, "Beef Patty"),
            ]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            assert order.total_price == Decimal("3.50")
            assert len(order.items.all()) == 1

    def test_create_new_order_large_quantity(self, app, test_user, sample_menu_items):
        """Test creating an order with large quantities."""
        with app.app_context():
            item_data = [(sample_menu_items[2], "1.00", 50, "Cheddar Cheese")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            assert order.total_price == Decimal("50.00")
            order_item = order.items.first()
            assert order_item.quantity == 50

    def test_create_new_order_without_menu_item_id(self, app, test_user):
        """Test creating an order with custom items (no menu_item_id)."""
        with app.app_context():
            item_data = [(None, "5.00", 1, "Custom Burger")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            assert order.total_price == Decimal("5.00")
            order_item = order.items.first()
            assert order_item.menu_item_id is None
            assert order_item.name == "Custom Burger"

    def test_create_new_order_decimal_prices(self, app, test_user, sample_menu_items):
        """Test creating an order with decimal prices."""
        with app.app_context():
            item_data = [
                (sample_menu_items[0], "1.99", 1, "Item 1"),
                (sample_menu_items[1], "2.49", 2, "Item 2"),
            ]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            # 1.99 + (2.49 * 2) = 6.97
            assert order.total_price == Decimal("6.97")

    def test_create_new_order_multiple_same_item(
        self, app, test_user, sample_menu_items
    ):
        """Test creating an order with multiple quantities of the same item."""
        with app.app_context():
            item_data = [(sample_menu_items[1], "3.50", 3, "Beef Patty")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            assert order.total_price == Decimal("10.50")  # 3.50 * 3
            order_item = order.items.first()
            assert order_item.quantity == 3

    def test_create_new_order_mixed_items(self, app, test_user, sample_menu_items):
        """Test creating an order with various items and quantities."""
        with app.app_context():
            item_data = [
                (sample_menu_items[0], "1.50", 1, "Classic Bun"),
                (sample_menu_items[1], "3.50", 2, "Beef Patty"),
                (sample_menu_items[2], "1.00", 2, "Cheddar Cheese"),
                (sample_menu_items[3], "0.50", 3, "Lettuce"),
                (sample_menu_items[4], "0.25", 1, "Ketchup"),
            ]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True
            # Calculation: 1.50 + (3.50*2) + (1.00*2) + (0.50*3) + 0.25
            # Total: 1.50 + 7.00 + 2.00 + 1.50 + 0.25 = 12.25
            assert order.total_price == Decimal("12.25")
            assert len(order.items.all()) == 5

    def test_create_new_order_verify_order_items(
        self, app, test_user, sample_menu_items
    ):
        """Test that order items are created with correct data."""
        with app.app_context():
            item_data = [
                (sample_menu_items[0], "1.50", 1, "Classic Bun"),
                (sample_menu_items[1], "3.50", 2, "Beef Patty"),
            ]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is True

            order_items = order.items.all()
            assert len(order_items) == 2

            # Check first item
            item1 = order_items[0]
            assert item1.menu_item_id == sample_menu_items[0]
            assert item1.name == "Classic Bun"
            assert item1.price == Decimal("1.50")
            assert item1.quantity == 1

            # Check second item
            item2 = order_items[1]
            assert item2.menu_item_id == sample_menu_items[1]
            assert item2.name == "Beef Patty"
            assert item2.price == Decimal("3.50")
            assert item2.quantity == 2

    def test_create_new_order_invalid_price_format(
        self, app, test_user, sample_menu_items
    ):
        """Test creating an order with invalid price format."""
        with app.app_context():
            item_data = [(sample_menu_items[0], "invalid", 1, "Classic Bun")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is False
            assert "Error placing order" in message
            assert order is None

    def test_create_new_order_invalid_quantity_format(
        self, app, test_user, sample_menu_items
    ):
        """Test creating an order with invalid quantity format."""
        with app.app_context():
            item_data = [(sample_menu_items[0], "1.50", "invalid", "Classic Bun")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is False
            assert "Error placing order" in message
            assert order is None

    def test_create_new_order_database_rollback(
        self, app, test_user, sample_menu_items
    ):
        """Test that database is rolled back on error."""
        with app.app_context():
            # Get initial order count
            initial_count = Order.query.count()

            # Try to create order with invalid data
            item_data = [(sample_menu_items[0], "invalid_price", 1, "Classic Bun")]

            success, message, order = OrderController.create_new_order(
                test_user, item_data
            )

            assert success is False
            # Verify no new orders were created
            final_count = Order.query.count()
            assert final_count == initial_count
