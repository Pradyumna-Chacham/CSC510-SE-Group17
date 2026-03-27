from flask_login import login_user
from controllers.menu_controller import MenuController
from models.menu_item import MenuItem
from database.db import db


class TestMenuController:
    """Test MenuController business logic"""

    def test_get_all_items_empty(self, app):
        """Test getting all items when database is empty"""
        # Ensure database is truly empty
        MenuItem.query.delete()
        db.session.commit()

        success, msg, items = MenuController.get_all_items()
        assert success is True
        assert items == []

    def test_get_all_items(self, app, multiple_menu_items):
        """Test getting all menu items"""
        success, msg, items = MenuController.get_all_items()
        assert success is True
        assert len(items) == 5

    def test_get_item_by_id_success(self, app, sample_menu_item):
        """Test getting item by valid ID"""
        success, msg, item = MenuController.get_item_by_id(sample_menu_item.id)
        assert success is True
        assert item.name == "Test Burger"

    def test_get_item_by_id_not_found(self, app):
        """Test getting item with invalid ID"""
        success, msg, item = MenuController.get_item_by_id(9999)
        assert success is False
        assert msg == "Item not found"
        assert item is None

    # ===== FIXED TESTS START HERE =====

    def test_create_item_unauthorized(self, app, customer_user):
        """Test that customers cannot create items"""
        with app.test_request_context():
            login_user(customer_user)
            success, msg, item = MenuController.create_item(
                name="New Item", category="bun", description="Test", price=1.99
            )
            assert success is False
            assert "Unauthorized" in msg

    def test_create_item_as_admin(self, app, admin_user):
        """Test admin can create items"""
        with app.test_request_context():
            login_user(admin_user)
            success, msg, item = MenuController.create_item(
                name="Admin Item",
                category="patty",
                description="Admin created",
                price=4.99,
                calories=300,
                protein=25,
            )
            assert success is True
            assert item.name == "Admin Item"

    def test_create_item_as_staff(self, app, staff_user):
        """Test staff can create items"""
        with app.test_request_context():
            login_user(staff_user)
            success, msg, item = MenuController.create_item(
                name="Staff Item",
                category="sauce",
                description="Staff created",
                price=0.75,
            )
            assert success is True
            assert item.name == "Staff Item"

    def test_create_item_missing_fields(self, app, admin_user):
        """Test creating item with missing required fields"""
        with app.test_request_context():
            login_user(admin_user)
            success, msg, item = MenuController.create_item(
                name="", category="bun", description="Test", price=1.99  # Missing name
            )
            assert success is False
            assert "required" in msg.lower()

    def test_update_item_as_admin(self, app, admin_user, sample_menu_item):
        """Test admin can update items"""
        with app.test_request_context():
            login_user(admin_user)
            success, msg, item = MenuController.update_item(
                item_id=sample_menu_item.id, name="Updated Name", price=7.99
            )
            assert success is True
            assert item.name == "Updated Name"
            assert float(item.price) == 7.99

    def test_delete_item_staff_unauthorized(self, app, staff_user, sample_menu_item):
        """Test that staff cannot delete items"""
        with app.test_request_context():
            login_user(staff_user)
            success, msg, _ = MenuController.delete_item(sample_menu_item.id)
            assert success is False
            assert "Unauthorized" in msg

    def test_delete_item_as_admin(self, app, admin_user, sample_menu_item):
        """Test admin can delete items"""
        with app.test_request_context():
            login_user(admin_user)
            item_id = sample_menu_item.id
            success, msg, _ = MenuController.delete_item(item_id)
            assert success is True

            # Verify it's deleted
            deleted_item = MenuItem.query.get(item_id)
            assert deleted_item is None

    def test_toggle_availability(self, app, admin_user, sample_menu_item):
        """Test toggling item availability"""
        with app.test_request_context():
            login_user(admin_user)
            original_status = sample_menu_item.is_available

            success, msg, item = MenuController.toggle_availability(sample_menu_item.id)
            assert success is True
            assert item.is_available != original_status

    def test_toggle_healthy_choice(self, app, staff_user, sample_menu_item):
        """Test toggling healthy choice status"""
        with app.test_request_context():
            login_user(staff_user)
            original_status = sample_menu_item.is_healthy_choice

            success, msg, item = MenuController.toggle_healthy_choice(
                sample_menu_item.id
            )
            assert success is True
            assert item.is_healthy_choice != original_status

    def test_get_items_by_category(self, app, multiple_menu_items):
        """Test getting items filtered by category"""
        success, msg, items = MenuController.get_items_by_category("patty")
        assert success is True
        assert len(items) == 2  # Beef and Turkey patties
        assert all(item.category == "patty" for item in items)

    def test_get_available_items(self, app, multiple_menu_items):
        """Test getting only available items"""
        success, msg, items = MenuController.get_available_items()
        assert success is True
        assert len(items) == 4  # Turkey Patty is unavailable
        assert all(item.is_available for item in items)

    def test_get_healthy_choices(self, app, multiple_menu_items):
        """Test getting healthy choice items"""
        success, msg, items = MenuController.get_healthy_choices()
        assert success is True
        assert len(items) == 1  # Only Lettuce is marked healthy
        assert items[0].name == "Lettuce"
        assert all(item.is_healthy_choice for item in items)
