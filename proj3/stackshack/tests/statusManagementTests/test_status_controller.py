from controllers.status_controller import StatusController
from models.order import Order


class TestStatusController:
    """Test cases for StatusController methods."""

    # ==================== UPDATE ORDER STATUS TESTS ====================

    def test_update_order_status_pending_to_preparing(self, app, pending_order):
        """Test updating order status from Pending to Preparing."""
        with app.app_context():
            success, msg, updated_order = StatusController.update_order_status(
                pending_order, "Preparing"
            )

            assert success is True
            assert "updated to Preparing" in msg
            assert updated_order.status == "Preparing"

            refreshed = Order.query.get(pending_order)
            assert refreshed.status == "Preparing"

    def test_update_order_status_preparing_to_ready(self, app, preparing_order):
        """Test updating order status from Preparing to Ready for Pickup."""
        with app.app_context():
            success, msg, updated_order = StatusController.update_order_status(
                preparing_order, "Ready for Pickup"
            )

            assert success is True
            assert "Ready for Pickup" in msg
            assert updated_order.status == "Ready for Pickup"

    def test_update_order_status_ready_to_delivered(self, app, ready_order):
        """Test updating order status from Ready for Pickup to Delivered."""
        with app.app_context():
            success, msg, updated_order = StatusController.update_order_status(
                ready_order, "Delivered"
            )

            assert success is True
            assert "Delivered" in msg
            assert updated_order.status == "Delivered"

    def test_update_order_status_invalid_transition(self, app, pending_order):
        """Test invalid status transition (Pending -> Ready for Pickup)."""
        with app.app_context():
            success, msg, order = StatusController.update_order_status(
                pending_order, "Ready for Pickup"
            )

            assert success is False
            assert "Invalid status transition" in msg or "transition" in msg.lower()

    def test_update_order_status_cannot_update_delivered(self, app, delivered_order):
        """Test cannot update status of delivered order."""
        with app.app_context():
            success, msg, order = StatusController.update_order_status(
                delivered_order, "Cancelled"
            )

            assert success is False
            assert "delivered" in msg.lower()

    def test_update_order_status_cannot_update_cancelled(self, app, cancelled_order):
        """Test cannot update status of cancelled order."""
        with app.app_context():
            success, msg, order = StatusController.update_order_status(
                cancelled_order, "Preparing"
            )

            assert success is False
            assert "cancelled" in msg.lower()

    def test_update_order_status_nonexistent_order(self, app):
        """Test updating status of nonexistent order."""
        with app.app_context():
            success, msg, order = StatusController.update_order_status(
                99999, "Preparing"
            )

            assert success is False

    # ==================== CANCEL ORDER TESTS ====================

    def test_cancel_pending_order(self, app, test_customer_user, pending_order):
        """Test cancelling a pending order."""
        with app.app_context():
            success, msg, cancelled = StatusController.cancel_order(
                pending_order, test_customer_user
            )

            assert success is True
            assert "cancelled successfully" in msg.lower()
            assert cancelled.status == "Cancelled"

    def test_cancel_preparing_order(self, app, test_customer_user, preparing_order):
        """Test cancelling a preparing order."""
        with app.app_context():
            success, msg, cancelled = StatusController.cancel_order(
                preparing_order, test_customer_user
            )

            assert success is True
            assert cancelled.status == "Cancelled"

    def test_cancel_ready_order(self, app, test_customer_user, ready_order):
        """Test cancelling a ready for pickup order."""
        with app.app_context():
            success, msg, cancelled = StatusController.cancel_order(
                ready_order, test_customer_user
            )

            assert success is True
            assert cancelled.status == "Cancelled"

    def test_cannot_cancel_delivered_order(
        self, app, test_customer_user, delivered_order
    ):
        """Test cannot cancel a delivered order."""
        with app.app_context():
            success, msg, order = StatusController.cancel_order(
                delivered_order, test_customer_user
            )

            assert success is False
            assert "delivered" in msg.lower()

    def test_cannot_cancel_already_cancelled_order(
        self, app, test_customer_user, cancelled_order
    ):
        """Test cannot cancel an already cancelled order."""
        with app.app_context():
            success, msg, order = StatusController.cancel_order(
                cancelled_order, test_customer_user
            )

            assert success is False
            assert "cancelled" in msg.lower()

    def test_cancel_order_wrong_user(
        self, app, test_customer_user, test_staff_user, pending_order
    ):
        """Test cannot cancel another user's order."""
        with app.app_context():
            success, msg, order = StatusController.cancel_order(
                pending_order, test_staff_user
            )

            assert success is False
            assert "not found" in msg.lower() or "access denied" in msg.lower()

    def test_cancel_nonexistent_order(self, app, test_customer_user):
        """Test cancelling nonexistent order."""
        with app.app_context():
            success, msg, order = StatusController.cancel_order(
                99999, test_customer_user
            )

            assert success is False

    # ==================== GET ORDER BY ID TESTS ====================

    def test_get_order_by_id_success(self, app, test_customer_user, pending_order):
        """Test retrieving order by ID."""
        with app.app_context():
            success, msg, order = StatusController.get_order_by_id(
                pending_order, test_customer_user
            )

            assert success is True
            assert order.id == pending_order
            assert order.status == "Pending"

    def test_get_order_by_id_wrong_user(self, app, test_staff_user, pending_order):
        """Test cannot retrieve another user's order."""
        with app.app_context():
            success, msg, order = StatusController.get_order_by_id(
                pending_order, test_staff_user
            )

            assert success is False
            assert order is None

    def test_get_order_by_id_nonexistent(self, app, test_customer_user):
        """Test retrieving nonexistent order."""
        with app.app_context():
            success, msg, order = StatusController.get_order_by_id(
                99999, test_customer_user
            )

            assert success is False
            assert order is None

    # ==================== GET ALL ORDERS FOR STAFF TESTS ====================

    def test_get_all_orders_for_staff(self, app, multiple_orders_various_statuses):
        """Test staff can retrieve all orders."""
        with app.app_context():
            success, msg, orders = StatusController.get_all_orders_for_staff()

            assert success is True
            assert len(orders) >= 4
            assert all(isinstance(o, Order) for o in orders)

    def test_get_all_orders_for_staff_ordering(
        self, app, multiple_orders_various_statuses
    ):
        """Test orders are returned in descending order by date."""
        with app.app_context():
            success, msg, orders = StatusController.get_all_orders_for_staff()

            assert success is True
            order_dates = [o.ordered_at for o in orders]
            assert order_dates == sorted(order_dates, reverse=True)

    def test_get_all_orders_no_orders(self, app):
        """Test getting all orders when none exist."""
        with app.app_context():
            success, msg, orders = StatusController.get_all_orders_for_staff()

            assert success is True
            assert len(orders) == 0

    # ==================== IS STAFF TESTS ====================

    def test_is_staff_true_for_staff(self, app, test_staff_user):
        """Test is_staff returns True for staff user."""
        with app.app_context():
            assert StatusController.is_staff(test_staff_user) is True

    def test_is_staff_true_for_admin(self, app, test_admin_user):
        """Test is_staff returns True for admin user."""
        with app.app_context():
            assert StatusController.is_staff(test_admin_user) is True

    def test_is_staff_false_for_customer(self, app, test_customer_user):
        """Test is_staff returns False for customer user."""
        with app.app_context():
            assert StatusController.is_staff(test_customer_user) is False

    def test_is_staff_nonexistent_user(self, app):
        """Test is_staff returns False for nonexistent user."""
        with app.app_context():
            assert StatusController.is_staff(99999) is False

    # ==================== GET STATUS FLOW TESTS ====================

    def test_get_status_flow_returns_dict(self, app):
        """Test get_status_flow returns proper dictionary."""
        with app.app_context():
            flow = StatusController.get_status_flow()

            assert isinstance(flow, dict)
            assert "Pending" in flow
            assert "Preparing" in flow
            assert "Ready for Pickup" in flow
            assert "Delivered" in flow
            assert "Cancelled" in flow

    def test_get_status_flow_has_required_fields(self, app):
        """Test each status has required fields."""
        with app.app_context():
            flow = StatusController.get_status_flow()

            for status, details in flow.items():
                assert "display" in details
                assert "icon" in details
                assert "nextStatuses" in details
                assert isinstance(details["display"], str)
                assert isinstance(details["icon"], str)
                assert isinstance(details["nextStatuses"], list)

    def test_status_flow_pending_has_preparing_next(self, app):
        """Test Pending status has Preparing as next status."""
        with app.app_context():
            flow = StatusController.get_status_flow()

            assert "Preparing" in flow["Pending"]["nextStatuses"]

    def test_status_flow_delivered_has_no_next(self, app):
        """Test Delivered status has no next statuses."""
        with app.app_context():
            flow = StatusController.get_status_flow()

            assert len(flow["Delivered"]["nextStatuses"]) == 0
