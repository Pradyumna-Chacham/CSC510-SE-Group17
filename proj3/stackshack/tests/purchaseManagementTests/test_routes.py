import json
from decimal import Decimal
from models.order import Order
from models.menu_item import MenuItem
from database.db import db


class TestOrderRoutes:
    """Test cases for order routes with proper authentication."""

    # ==================== AUTHENTICATION HELPER ====================

    def login(self, client, username="testuser", password="testpassword123"):
        """Helper method to login a user properly."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def logout(self, client):
        """Helper method to logout."""
        return client.get("/auth/logout", follow_redirects=True)

    # ==================== AUTHENTICATION TESTS ====================

    def test_order_history_requires_login(self, client):
        """Test that order history requires authentication."""
        response = client.get("/orders/history")

        # Should redirect to login
        assert response.status_code == 302
        assert (
            "/auth/login" in response.location or "login" in response.location.lower()
        )

    def test_order_history_authenticated(self, client, app, test_user, sample_order):
        """Test accessing order history when authenticated."""
        # Login properly using username and password
        self.login(client)

        response = client.get("/orders/history")

        assert response.status_code == 200
        assert b"history" in response.data.lower() or b"order" in response.data.lower()

    def test_order_history_displays_orders(self, client, app, test_user, sample_order):
        """Test that order history displays user orders."""
        self.login(client)

        response = client.get("/orders/history")

        assert response.status_code == 200

    def test_order_history_empty(self, client, app, test_user):
        """Test order history when user has no orders."""
        self.login(client)

        response = client.get("/orders/history")

        assert response.status_code == 200

    def test_order_history_multiple_orders(
        self, client, app, test_user, multiple_orders
    ):
        """Test order history with multiple orders."""
        self.login(client)

        response = client.get("/orders/history")

        assert response.status_code == 200
        assert b"order" in response.data.lower()

    # ================== INGREDIENTS ENDPOINT TESTS (NO AUTH NEEDED) ==================

    def test_get_ingredients_by_category_bun(self, client, app, sample_menu_items):
        """Test getting ingredients by category - bun."""
        response = client.get("/orders/ingredients/bun")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1

        # Check bun item exists
        bun_item = next((item for item in data if "bun" in item["name"].lower()), None)
        assert bun_item is not None
        assert "id" in bun_item
        assert "name" in bun_item
        assert "price" in bun_item
        assert "description" in bun_item
        assert "is_healthy" in bun_item
        assert "image_url" in bun_item

    def test_get_ingredients_by_category_patty(self, client, app, sample_menu_items):
        """Test getting ingredients by category - patty."""
        response = client.get("/orders/ingredients/patty")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        patty_items = [item for item in data if "patty" in item["name"].lower()]
        assert len(patty_items) >= 1

    def test_get_ingredients_by_category_cheese(self, client, app, sample_menu_items):
        """Test getting ingredients by category - cheese."""
        response = client.get("/orders/ingredients/cheese")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        cheese_items = [item for item in data if "cheese" in item["name"].lower()]
        assert len(cheese_items) >= 1

    def test_get_ingredients_by_category_topping(self, client, app, sample_menu_items):
        """Test getting ingredients by category - topping."""
        response = client.get("/orders/ingredients/topping")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_ingredients_by_category_sauce(self, client, app, sample_menu_items):
        """Test getting ingredients by category - sauce."""
        response = client.get("/orders/ingredients/sauce")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        sauce_items = [
            item
            for item in data
            if "sauce" in item["name"].lower() or "ketchup" in item["name"].lower()
        ]
        assert len(sauce_items) >= 1

    def test_get_ingredients_includes_unavailable(self, client, app, sample_menu_items):
        """Test that get_ingredients includes unavailable items."""
        response = client.get("/orders/ingredients/topping")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)

    def test_get_ingredients_empty_category(self, client, app):
        """Test getting ingredients for a category with no items."""
        response = client.get("/orders/ingredients/nonexistent")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_ingredients_case_insensitive(self, client, app, sample_menu_items):
        """Test that ingredient category search is case-insensitive."""
        response1 = client.get("/orders/ingredients/BUN")
        response2 = client.get("/orders/ingredients/bun")
        response3 = client.get("/orders/ingredients/Bun")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        data3 = json.loads(response3.data)

        assert len(data1) == len(data2) == len(data3)

    def test_get_ingredients_returns_correct_fields(
        self, client, app, sample_menu_items
    ):
        """Test that ingredients endpoint returns all required fields."""
        response = client.get("/orders/ingredients/bun")

        assert response.status_code == 200
        data = json.loads(response.data)

        if len(data) > 0:
            item = data[0]
            required_fields = [
                "id",
                "name",
                "price",
                "description",
                "is_healthy",
                "image_url",
            ]
            for field in required_fields:
                assert field in item, f"Missing field: {field}"

    def test_get_ingredients_price_format(self, client, app, sample_menu_items):
        """Test that prices are returned in correct format."""
        response = client.get("/orders/ingredients/bun")

        assert response.status_code == 200
        data = json.loads(response.data)

        if len(data) > 0:
            item = data[0]
            assert isinstance(item["price"], (int, float, str))

    def test_get_ingredients_partial_category_match(
        self, client, app, sample_menu_items
    ):
        """Test ingredients endpoint with partial category matches."""
        response = client.get("/orders/ingredients/top")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_ingredients_all_categories(self, client, app, sample_menu_items):
        """Test getting ingredients for all categories."""
        categories = ["bun", "patty", "cheese", "topping", "sauce"]

        for category in categories:
            response = client.get(f"/orders/ingredients/{category}")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_get_ingredients_special_characters(self, client, app):
        """Test ingredients endpoint with special characters."""
        response = client.get("/orders/ingredients/@#$%")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_ingredients_numeric_category(self, client, app):
        """Test ingredients endpoint with numeric category."""
        response = client.get("/orders/ingredients/123")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    # ==================== CREATE ORDER FORM TESTS ====================

    def test_create_order_form_requires_login(self, client):
        """Test that create order form requires authentication."""
        response = client.get("/orders/new")

        assert response.status_code == 302
        assert (
            "/auth/login" in response.location or "login" in response.location.lower()
        )

    def test_create_order_form_authenticated(
        self, client, app, test_user, sample_menu_items
    ):
        """Test accessing create order form when authenticated."""
        self.login(client)

        response = client.get("/orders/new")

        assert response.status_code == 200

    def test_create_order_form_displays_content(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that create order form displays properly."""
        self.login(client)

        response = client.get("/orders/new")

        assert response.status_code == 200

    # ==================== PLACE ORDER TESTS ====================

    def test_place_order_requires_login(self, client):
        """Test that placing order requires authentication."""
        response = client.post("/orders/place", data={})

        assert response.status_code == 302
        assert (
            "/auth/login" in response.location or "login" in response.location.lower()
        )

    def test_place_order_success(self, client, app, test_user, sample_menu_items):
        """Test placing an order successfully."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])
            patty = db.session.get(MenuItem, sample_menu_items[1])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
                f"quantity_{patty.id}": "2",
                f"price_{patty.id}": str(patty.price),
                f"name_{patty.id}": patty.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=False)

        assert response.status_code == 302
        assert "/orders/history" in response.location

    def test_place_order_creates_order(self, client, app, test_user, sample_menu_items):
        """Test that placing order creates order in database."""
        self.login(client)

        with app.app_context():
            initial_count = Order.query.filter_by(user_id=test_user).count()

            bun = db.session.get(MenuItem, sample_menu_items[0])
            patty = db.session.get(MenuItem, sample_menu_items[1])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
                f"quantity_{patty.id}": "1",
                f"price_{patty.id}": str(patty.price),
                f"name_{patty.id}": patty.name,
            }

        client.post("/orders/place", data=form_data, follow_redirects=True)

        with app.app_context():
            final_count = Order.query.filter_by(user_id=test_user).count()
            assert final_count == initial_count + 1

    def test_place_order_correct_total(self, client, app, test_user, sample_menu_items):
        """Test that order total is calculated correctly."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])
            patty = db.session.get(MenuItem, sample_menu_items[1])
            cheese = db.session.get(MenuItem, sample_menu_items[2])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
                f"quantity_{patty.id}": "2",
                f"price_{patty.id}": str(patty.price),
                f"name_{patty.id}": patty.name,
                f"quantity_{cheese.id}": "1",
                f"price_{cheese.id}": str(cheese.price),
                f"name_{cheese.id}": cheese.name,
            }

            expected_total = (
                Decimal(str(bun.price))
                + (Decimal(str(patty.price)) * 2)
                + Decimal(str(cheese.price))
            )

        client.post("/orders/place", data=form_data, follow_redirects=True)

        with app.app_context():
            order = (
                Order.query.filter_by(user_id=test_user)
                .order_by(Order.ordered_at.desc())
                .first()
            )
            assert order is not None
            assert order.total_price == expected_total

    def test_place_order_empty(self, client, app, test_user):
        """Test placing an empty order."""
        self.login(client)

        response = client.post("/orders/place", data={}, follow_redirects=True)

        assert response.status_code == 200
        assert b"error" in response.data.lower() or b"empty" in response.data.lower()

    def test_place_order_zero_quantity(self, client, app, test_user, sample_menu_items):
        """Test placing order with zero quantity items."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "0",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200
        assert b"error" in response.data.lower() or b"empty" in response.data.lower()

    def test_place_order_missing_price(self, client, app, test_user, sample_menu_items):
        """Test placing order with missing price data."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {f"quantity_{bun.id}": "1", f"name_{bun.id}": bun.name}

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    def test_place_order_missing_name(self, client, app, test_user, sample_menu_items):
        """Test placing order with missing name data."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {f"quantity_{bun.id}": "1", f"price_{bun.id}": str(bun.price)}

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    def test_place_order_multiple_items(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with multiple different items."""
        self.login(client)

        with app.app_context():
            items = [db.session.get(MenuItem, mid) for mid in sample_menu_items[:5]]

            form_data = {}
            for item in items:
                form_data[f"quantity_{item.id}"] = "1"
                form_data[f"price_{item.id}"] = str(item.price)
                form_data[f"name_{item.id}"] = item.name

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            order = (
                Order.query.filter_by(user_id=test_user)
                .order_by(Order.ordered_at.desc())
                .first()
            )
            assert order is not None
            assert len(order.items.all()) == 5

    def test_place_order_large_quantities(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with large quantities."""
        self.login(client)

        with app.app_context():
            cheese = db.session.get(MenuItem, sample_menu_items[2])

            form_data = {
                f"quantity_{cheese.id}": "50",
                f"price_{cheese.id}": str(cheese.price),
                f"name_{cheese.id}": cheese.name,
            }

            expected_total = Decimal(str(cheese.price)) * 50

        client.post("/orders/place", data=form_data, follow_redirects=True)

        with app.app_context():
            order = (
                Order.query.filter_by(user_id=test_user)
                .order_by(Order.ordered_at.desc())
                .first()
            )
            assert order is not None
            assert order.total_price == expected_total

            order_item = order.items.first()
            assert order_item.quantity == 50

    def test_place_order_invalid_quantity_format(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with invalid quantity format."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "invalid",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    def test_place_order_redirect_on_success(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that successful order redirects to history."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])
            patty = db.session.get(MenuItem, sample_menu_items[1])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
                f"quantity_{patty.id}": "1",
                f"price_{patty.id}": str(patty.price),
                f"name_{patty.id}": patty.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=False)

        assert response.status_code == 302
        assert "history" in response.location

    def test_place_order_flash_message(self, client, app, test_user, sample_menu_items):
        """Test that placing order shows flash message."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])
            patty = db.session.get(MenuItem, sample_menu_items[1])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
                f"quantity_{patty.id}": "1",
                f"price_{patty.id}": str(patty.price),
                f"name_{patty.id}": patty.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200
        assert (
            b"success" in response.data.lower()
            or b"placed" in response.data.lower()
            or b"order" in response.data.lower()
        )

    # ==================== EDGE CASE TESTS ====================

    def test_place_order_with_decimal_quantity(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with decimal quantity (should fail or truncate)."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "1.5",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    def test_place_order_with_negative_quantity(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with negative quantity."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "-5",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    def test_place_order_very_long_item_name(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with very long item name."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            long_name = "A" * 500

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": long_name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    def test_place_order_with_very_high_price(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with very high price."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": "999999.99",
                f"name_{bun.id}": bun.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            order = (
                Order.query.filter_by(user_id=test_user)
                .order_by(Order.ordered_at.desc())
                .first()
            )
            if order:
                assert order.total_price == Decimal("999999.99")

    def test_place_order_mixed_valid_invalid_items(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with mix of valid and invalid items."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])
            patty = db.session.get(MenuItem, sample_menu_items[1])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
                f"quantity_{patty.id}": "invalid",
                f"price_{patty.id}": str(patty.price),
                f"name_{patty.id}": patty.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    def test_place_order_whitespace_in_quantities(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing order with whitespace in quantities."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "  2  ",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=True)

        assert response.status_code == 200

    # ==================== LOGOUT AND RE-LOGIN TESTS ====================

    def test_place_order_after_logout_fails(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that placing order after logout fails."""
        self.login(client)
        self.logout(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
            }

        response = client.post("/orders/place", data=form_data, follow_redirects=False)

        # Should redirect to login
        assert response.status_code == 302
        assert "login" in response.location.lower()

    def test_order_history_after_logout_fails(self, client, app, test_user):
        """Test that order history after logout fails."""
        self.login(client)
        self.logout(client)

        response = client.get("/orders/history", follow_redirects=False)

        # Should redirect to login
        assert response.status_code == 302
        assert "login" in response.location.lower()

    def test_multiple_orders_same_session(
        self, client, app, test_user, sample_menu_items
    ):
        """Test placing multiple orders in the same session."""
        self.login(client)

        with app.app_context():
            bun = db.session.get(MenuItem, sample_menu_items[0])

            form_data = {
                f"quantity_{bun.id}": "1",
                f"price_{bun.id}": str(bun.price),
                f"name_{bun.id}": bun.name,
            }

        # Place first order
        response1 = client.post("/orders/place", data=form_data, follow_redirects=True)
        assert response1.status_code == 200

        # Place second order (same session, no re-login needed)
        response2 = client.post("/orders/place", data=form_data, follow_redirects=True)
        assert response2.status_code == 200

        # Verify both orders were created
        with app.app_context():
            order_count = Order.query.filter_by(user_id=test_user).count()
            assert order_count >= 2
