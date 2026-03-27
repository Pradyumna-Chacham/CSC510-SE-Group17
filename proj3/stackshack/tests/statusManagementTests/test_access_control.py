import json
from models.order import Order
from models.user import User
from database.db import db


class TestStatusAccessControl:
    """Test cases for access control in status management."""

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

    # ==================== MANAGE ORDERS ACCESS CONTROL ====================

    def test_manage_orders_unauthenticated_redirect(self, client):
        """Test unauthenticated user redirected from manage orders."""
        response = client.get("/status/manage")
        assert response.status_code == 302

    def test_manage_orders_customer_cannot_access(self, client, test_customer_user):
        """Test customer role cannot access manage orders."""
        self.login(client, "customer1", "password123")
        response = client.get("/status/manage")
        assert response.status_code == 302

    def test_manage_orders_staff_can_access(self, client, test_staff_user):
        """Test staff role can access manage orders."""
        self.login(client, "staff1", "staffpass123")
        response = client.get("/status/manage")
        assert response.status_code == 200

    def test_manage_orders_admin_can_access(self, client, test_admin_user):
        """Test admin role can access manage orders."""
        self.login(client, "admin1", "adminpass123")
        response = client.get("/status/manage")
        assert response.status_code == 200

    # ==================== UPDATE STATUS ACCESS CONTROL ====================

    def test_update_status_unauthenticated_denied(self, client):
        """Test unauthenticated user cannot update status."""
        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": 1, "status": "Preparing"}),
            content_type="application/json",
        )
        assert response.status_code == 302

    def test_update_status_customer_cannot_update_any_order(
        self, client, app, test_customer_user, test_staff_user
    ):
        """Test customer cannot update any order status (must be staff)."""
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
            order_id = order.id

        self.login(client, "customer1", "password123")
        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": order_id, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 403
        data = json.loads(response.data)
        assert data["success"] is False
        assert "staff" in data["message"].lower()

    def test_update_status_staff_can_update_any_order(
        self, client, app, test_staff_user, pending_order
    ):
        """Test staff can update any order status."""
        self.login(client, "staff1", "staffpass123")
        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": pending_order, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_update_status_admin_can_update_any_order(
        self, client, app, test_admin_user, pending_order
    ):
        """Test admin can update any order status."""
        self.login(client, "admin1", "adminpass123")
        response = client.post(
            "/status/update",
            data=json.dumps({"order_id": pending_order, "status": "Preparing"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_customer_can_view_own_order(
        self, client, app, test_customer_user, pending_order
    ):
        """Test customer can view their own order status."""
        self.login(client, "customer1", "password123")
        response = client.get("/orders/history")

        assert response.status_code == 200

    # ==================== CANCEL ORDER ACCESS CONTROL ====================

    def test_cancel_order_unauthenticated_denied(self, client):
        """Test unauthenticated user cannot cancel order."""
        response = client.post("/status/cancel/1")
        assert response.status_code == 302

    def test_cancel_order_customer_can_cancel_own(
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

    def test_cancel_order_customer_cannot_cancel_other(
        self, client, app, test_customer_user, test_staff_user
    ):
        """Test customer cannot cancel another user's order."""
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

    def test_cancel_order_staff_cannot_cancel_through_route(
        self, client, app, test_staff_user, test_customer_user, pending_order
    ):
        """Test staff cannot cancel through user cancel route (only customers)."""
        self.login(client, "staff1", "staffpass123")
        response = client.post(
            f"/status/cancel/{pending_order}", content_type="application/json"
        )

        assert response.status_code == 400

    # ==================== STATUS FLOW ENDPOINT ACCESS ====================

    def test_status_flow_public_endpoint(self, client):
        """Test status flow endpoint is publicly accessible."""
        response = client.get("/status/flow")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_status_flow_authenticated_user(self, client, test_customer_user):
        """Test status flow accessible by authenticated users."""
        self.login(client, "customer1", "password123")
        response = client.get("/status/flow")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    # ==================== ROLE-BASED WORKFLOW TESTS ====================

    def test_full_workflow_staff_managing_order(
        self, client, app, test_staff_user, pending_order
    ):
        """Test complete workflow: staff updates order through all states."""
        self.login(client, "staff1", "staffpass123")

        transitions = [
            ("Preparing", 200),
            ("Ready for Pickup", 200),
            ("Delivered", 200),
        ]

        current_order_id = pending_order
        for new_status, expected_code in transitions:
            response = client.post(
                "/status/update",
                data=json.dumps({"order_id": current_order_id, "status": new_status}),
                content_type="application/json",
            )

            assert response.status_code == expected_code
            data = json.loads(response.data)
            assert data["success"] is True

    def test_full_workflow_customer_viewing_order(
        self, client, app, test_customer_user, pending_order
    ):
        """Test customer can view order without updating it."""
        self.login(client, "customer1", "password123")

        response = client.get("/orders/history")
        assert response.status_code == 200

        response = client.get("/status/flow")
        assert response.status_code == 200

    def test_isolation_multiple_users(self, client, app):
        """Test orders are isolated between different users."""
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

            user1 = User(username="user1")
            user1.set_password("pass1")
            user1.role = "customer"
            db.session.add(user1)
            db.session.flush()

            user2 = User(username="user2")
            user2.set_password("pass2")
            user2.role = "customer"
            db.session.add(user2)
            db.session.flush()

            order1 = Order(
                user_id=user1.id, total_price=Decimal("5.00"), status="Pending"
            )
            order2 = Order(
                user_id=user2.id, total_price=Decimal("5.00"), status="Pending"
            )
            db.session.add(order1)
            db.session.add(order2)
            db.session.flush()

            for order in [order1, order2]:
                item_obj = MenuItem.query.first()
                oi = OrderItem(
                    order_id=order.id,
                    menu_item_id=item_obj.id,
                    name=item_obj.name,
                    price=item_obj.price,
                    quantity=1,
                )
                db.session.add(oi)

            db.session.commit()
            # order1_id = order1.id
            order2_id = order2.id

        self.login(client, "user1", "pass1")
        response = client.post(
            f"/status/cancel/{order2_id}", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
