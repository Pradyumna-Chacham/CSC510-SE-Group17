import json
from models.order import Order
from database.db import db


class TestStatusRoutes:
    """Test cases for status management routes."""

    def login(self, client, username, password):
        """Helper method to login a user."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def logout(self, client):
        """Helper method to logout."""
        return client.get("/auth/logout", follow_redirects=True)

    # ==================== MANAGE ORDERS ROUTE TESTS ====================

    def test_manage_orders_requires_login(self, client):
        """Test manage orders requires authentication."""
        response = client.get("/status/manage")

        assert response.status_code == 302

    def test_manage_orders_staff_access(
        self, client, app, test_staff_user, pending_order
    ):
        """Test staff can access manage orders page."""
        self.login(client, "staff1", "staffpass123")

        response = client.get("/status/manage")

        assert response.status_code == 200
        assert b"manage" in response.data.lower() or b"order" in response.data.lower()

    def test_manage_orders_admin_access(
        self, client, app, test_admin_user, pending_order
    ):
        """Test admin can access manage orders page."""
        self.login(client, "admin1", "adminpass123")

        response = client.get("/status/manage")

        assert response.status_code == 200

    def test_manage_orders_customer_denied(
        self, client, app, test_customer_user, pending_order
    ):
        """Test customer cannot access manage orders page."""
        self.login(client, "customer1", "password123")

        response = client.get("/status/manage")

        assert response.status_code == 302

    def test_manage_orders_shows_all_orders(
        self,
        client,
        app,
        test_staff_user,
        test_customer_user,
        multiple_orders_various_statuses,
    ):
        """Test manage orders displays all orders."""
        self.login(client, "staff1", "staffpass123")

        response = client.get("/status/manage")

        assert response.status_code == 200

    # ==================== UPDATE STATUS ROUTE TESTS ====================

    def test_update_status_requires_login(self, client):
        """Test update status requires authentication."""
        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": 1, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 302

    def test_update_status_staff_success(
        self, client, app, test_staff_user, pending_order
    ):
        """Test staff can update order status."""
        self.login(client, "staff1", "staffpass123")

        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": pending_order, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["order"]["status"] == "Preparing"

        with app.app_context():
            order = Order.query.get(pending_order)
            assert order.status == "Preparing"

    def test_update_status_customer_own_order(
        self, client, app, test_customer_user, pending_order
    ):
        """Test customer cannot update even their own order status."""
        self.login(client, "customer1", "password123")

        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": pending_order, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 403
        data = json.loads(response.data)
        assert data["success"] is False
        assert "staff" in data["message"].lower()

    def test_update_status_customer_other_order(
        self, client, app, test_customer_user, test_staff_user
    ):
        """Test customer cannot update another user's order (only staff can)."""
        with app.app_context():
            from models.menu_item import MenuItem
            from decimal import Decimal

            item = MenuItem.query.first()
            if not item:
                item = MenuItem(
                    name="Test Item",
                    description="Test",
                    price=Decimal("5.00"),
                    category="test",
                    is_available=True,
                    is_healthy_choice=False,
                    image_url="/test.png",
                )
                db.session.add(item)
                db.session.flush()

            from models.order import OrderItem

            order = Order(
                user_id=test_staff_user, total_price=Decimal("5.00"), status="Pending"
            )
            db.session.add(order)
            db.session.flush()

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                name=item.name,
                price=item.price,
                quantity=1,
            )
            db.session.add(order_item)
            db.session.commit()
            other_order_id = order.id

        self.login(client, "customer1", "password123")

        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": other_order_id, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 403
        data = json.loads(response.data)
        assert data["success"] is False
        assert "staff" in data["message"].lower()

    def test_update_status_invalid_transition(
        self, client, app, test_staff_user, pending_order
    ):
        """Test invalid status transition is rejected."""
        self.login(client, "staff1", "staffpass123")

        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": pending_order, "status": "Ready for Pickup"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Invalid" in data["message"] or "transition" in data["message"].lower()

    def test_update_status_missing_fields(self, client, test_staff_user):
        """Test update status with missing fields."""
        self.login(client, "staff1", "staffpass123")

        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": 1}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_update_status_nonexistent_order(self, client, test_staff_user):
        """Test updating nonexistent order."""
        self.login(client, "staff1", "staffpass123")

        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": 99999, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False

    # ==================== CANCEL ORDER ROUTE TESTS ====================

    def test_cancel_order_requires_login(self, client):
        """Test cancel order requires authentication."""
        response = client.post("/status/cancel/1")

        assert response.status_code == 302

    def test_cancel_order_customer_success(
        self, client, app, test_customer_user, pending_order
    ):
        """Test customer can cancel their own order."""
        self.login(client, "customer1", "password123")

        response = client.post(
            f"/status/cancel/{pending_order}", content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["order"]["status"] == "Cancelled"

        with app.app_context():
            order = Order.query.get(pending_order)
            assert order.status == "Cancelled"

    def test_cancel_order_staff_success(
        self, client, app, test_staff_user, test_customer_user, pending_order
    ):
        """Test staff cannot cancel customer's order through cancel endpoint."""
        self.login(client, "staff1", "staffpass123")

        response = client.post(
            f"/status/cancel/{pending_order}", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_cannot_cancel_delivered_order(
        self, client, app, test_customer_user, delivered_order
    ):
        """Test cannot cancel delivered order."""
        self.login(client, "customer1", "password123")

        response = client.post(
            f"/status/cancel/{delivered_order}", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "delivered" in data["message"].lower()

    def test_cannot_cancel_already_cancelled(
        self, client, app, test_customer_user, cancelled_order
    ):
        """Test cannot cancel already cancelled order."""
        self.login(client, "customer1", "password123")

        response = client.post(
            f"/status/cancel/{cancelled_order}", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "cancelled" in data["message"].lower()

    def test_cancel_nonexistent_order(self, client, test_customer_user):
        """Test cancelling nonexistent order."""
        self.login(client, "customer1", "password123")

        response = client.post("/status/cancel/99999", content_type="application/json")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_cancel_other_user_order(
        self, client, app, test_customer_user, test_staff_user
    ):
        """Test cannot cancel another user's order."""
        with app.app_context():
            from models.menu_item import MenuItem
            from models.order import OrderItem
            from decimal import Decimal

            item = MenuItem.query.first()
            if not item:
                item = MenuItem(
                    name="Test Item",
                    description="Test",
                    price=Decimal("5.00"),
                    category="test",
                    is_available=True,
                    is_healthy_choice=False,
                    image_url="/test.png",
                )
                db.session.add(item)
                db.session.flush()

            order = Order(
                user_id=test_staff_user, total_price=Decimal("5.00"), status="Pending"
            )
            db.session.add(order)
            db.session.flush()

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                name=item.name,
                price=item.price,
                quantity=1,
            )
            db.session.add(order_item)
            db.session.commit()
            other_order_id = order.id

        self.login(client, "customer1", "password123")

        response = client.post(
            f"/status/cancel/{other_order_id}", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    # ==================== STATUS FLOW ENDPOINT TESTS ====================

    def test_get_status_flow_no_auth_required(self, client):
        """Test status flow endpoint accessible without authentication."""
        response = client.get("/status/flow")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "flow" in data

    def test_get_status_flow_has_all_statuses(self, client):
        """Test status flow includes all statuses."""
        response = client.get("/status/flow")

        data = json.loads(response.data)
        flow = data["flow"]

        assert "Pending" in flow
        assert "Preparing" in flow
        assert "Ready for Pickup" in flow
        assert "Delivered" in flow
        assert "Cancelled" in flow

    def test_get_status_flow_structure(self, client):
        """Test status flow response structure."""
        response = client.get("/status/flow")

        data = json.loads(response.data)
        flow = data["flow"]

        for status, details in flow.items():
            assert "display" in details
            assert "icon" in details
            assert "nextStatuses" in details
