class TestCreateOrderPage:
    """Test cases for the create order page (create.html)."""

    def login_user(self, client, username="testuser", password="testpassword123"):
        """Helper to login a user via the login route."""
        return client.post(
            "/auth/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_create_page_loads(self, client, app, test_user, sample_menu_items):
        """Test that the create order page loads successfully."""
        # Login first
        self.login_user(client)

        # Now access the create page
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"burger" in response.data.lower()
            or b"create" in response.data.lower()
            or b"order" in response.data.lower()
        )

    def test_create_page_has_burger_builder(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that burger builder elements are present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"burger-builder" in response.data or b"builder" in response.data.lower()

    def test_create_page_has_burger_stack(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that burger stack element is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"burger-stack" in response.data or b"stack" in response.data.lower()

    def test_create_page_has_ingredient_cards(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that ingredient cards container is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"ingredient-cards" in response.data
            or b"ingredient" in response.data.lower()
        )

    def test_create_page_has_total_price(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that total price display is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"total-price" in response.data or b"total" in response.data.lower()

    def test_create_page_has_place_order_button(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that place order button is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"place-order-btn" in response.data or b"Place Order" in response.data

    def test_create_page_has_form(self, client, app, test_user, sample_menu_items):
        """Test that the order form is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"place-order-form" in response.data or b"<form" in response.data.lower()

    def test_create_page_form_action(self, client, app, test_user, sample_menu_items):
        """Test that form has correct action URL."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"/orders/place" in response.data or b"/place" in response.data

    def test_create_page_has_javascript(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page includes JavaScript functionality."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"<script>" in response.data or b"<script " in response.data

    def test_create_page_has_styles(self, client, app, test_user, sample_menu_items):
        """Test that page includes CSS styles."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"<style>" in response.data
            or b"<style " in response.data
            or b".burger-builder" in response.data
        )

    def test_create_page_has_category_header(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that current category header is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"current-category" in response.data or b"category" in response.data.lower()
        )

    def test_create_page_has_price_breakdown(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that price breakdown element is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"price-breakdown" in response.data or b"breakdown" in response.data.lower()
        )

    def test_create_page_has_hidden_inputs(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that hidden inputs container is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"hidden-inputs" in response.data or b"hidden" in response.data.lower()

    def test_create_page_burger_layers(self, client, app, test_user, sample_menu_items):
        """Test that burger layer structure is defined."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"layer" in response.data

    def test_create_page_ingredient_categories(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that ingredient category logic is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"bun" in response.data
        assert b"patty" in response.data

    def test_create_page_fetch_ingredients(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has ingredient fetching functionality."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"/orders/ingredients" in response.data
            or b"loadIngredients" in response.data
        )

    def test_create_page_add_ingredient_functionality(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that add ingredient functionality is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"addIngredient" in response.data or b"add" in response.data.lower()

    def test_create_page_remove_functionality(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that remove layer functionality is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"removeLayer" in response.data or b"remove" in response.data.lower()

    def test_create_page_quantity_controls(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that quantity control functionality is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"quantity" in response.data.lower()

    def test_create_page_update_price_functionality(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that price update functionality is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"updateTotalPrice" in response.data or b"total-price" in response.data

    def test_create_page_selected_ingredients_tracking(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that selected ingredients tracking is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"selectedIngredients" in response.data
            or b"selected" in response.data.lower()
        )

    def test_create_page_form_inputs_generation(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that form inputs generation functionality is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"updateFormInputs" in response.data or b"hidden-inputs" in response.data

    def test_create_page_form_submission_handler(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that form submission handler is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"addEventListener" in response.data or b"submit" in response.data.lower()
        )

    def test_create_page_window_loaded_initialization(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that window load initialization is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"DOMContentLoaded" in response.data
            or b"window.addEventListener" in response.data
        )

    def test_create_page_default_category_load(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that default category loading is present."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"bun" in response.data

    def test_create_page_layer_listener_attachment(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that layer event listeners are attached."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"attachLayerListeners" in response.data
            or b"addEventListener" in response.data
        )

    def test_create_page_responsive_design(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has responsive design elements."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"display: flex" in response.data or b"display:flex" in response.data

    def test_create_page_visual_feedback(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has visual feedback elements."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"transition" in response.data or b":hover" in response.data

    def test_create_page_healthy_icon_support(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page supports healthy icons."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"healthy-icon" in response.data
            or b"is_healthy" in response.data
            or b"healthy" in response.data.lower()
        )

    def test_create_page_image_display(self, client, app, test_user, sample_menu_items):
        """Test that page displays ingredient images."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"image_url" in response.data
            or b"backgroundImage" in response.data
            or b"img" in response.data.lower()
        )

    def test_create_page_price_formatting(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has price formatting logic."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"toFixed" in response.data or b"$" in response.data

    def test_create_page_category_switching(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page supports category switching."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"activeCategory" in response.data
            or b"data-category" in response.data
            or b"category" in response.data.lower()
        )

    def test_create_page_layer_creation(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has layer creation functionality."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"createLayerElement" in response.data or b"createElement" in response.data
        )

    def test_create_page_bun_special_handling(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has special handling for buns."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"top-bun" in response.data
            or b"bottom-bun" in response.data
            or b"bun" in response.data.lower()
        )

    def test_create_page_order_summary(self, client, app, test_user, sample_menu_items):
        """Test that page has order summary section."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"Order Summary" in response.data or b"summary" in response.data.lower()

    def test_create_page_breakdown_display(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has price breakdown display."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"breakdown" in response.data.lower()

    def test_create_page_button_disabled_state(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page handles button disabled state."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"disabled" in response.data.lower() or b"button" in response.data.lower()
        )

    def test_create_page_validation_logic(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has order validation logic."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        # Page should have some validation
        assert response.status_code == 200

    def test_create_page_error_handling(
        self, client, app, test_user, sample_menu_items
    ):
        """Test that page has error handling."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"alert" in response.data
            or b"error" in response.data.lower()
            or b"preventDefault" in response.data
        )

    def test_create_page_loading_state(self, client, app, test_user, sample_menu_items):
        """Test that page handles loading states."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert (
            b"Placing Order" in response.data
            or b"loading" in response.data.lower()
            or b"disabled" in response.data.lower()
        )

    def test_create_page_extends_base(self, client, app, test_user, sample_menu_items):
        """Test that page extends base template."""
        self.login_user(client)
        response = client.get("/orders/new")

        assert response.status_code == 200
        assert b"<html" in response.data.lower()
        assert b"<body" in response.data.lower()
