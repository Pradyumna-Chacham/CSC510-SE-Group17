from models.menu_item import MenuItem
from database.db import db


class TestMenuItemModel:
    """Test MenuItem model"""

    def test_create_menu_item(self, app):
        """Test creating a basic menu item"""
        item = MenuItem(
            name="Test Bun", category="bun", price=1.99, calories=150, protein=5
        )
        db.session.add(item)
        db.session.commit()

        assert item.id is not None
        assert item.name == "Test Bun"
        assert item.category == "bun"
        assert float(item.price) == 1.99

    def test_menu_item_defaults(self, app):
        """Test default values for menu item"""
        item = MenuItem(name="Test Item", category="topping", price=0.50)
        db.session.add(item)
        db.session.commit()

        assert item.is_available is True
        assert item.is_healthy_choice is False
        assert item.calories is None
        assert item.protein is None

    def test_menu_item_all_fields(self, app):
        """Test creating menu item with all fields"""
        item = MenuItem(
            name="Premium Burger",
            category="patty",
            description="High quality beef",
            price=5.99,
            calories=400,
            protein=30,
            is_available=True,
            is_healthy_choice=False,
            image_url="http://example.com/burger.jpg",
        )
        db.session.add(item)
        db.session.commit()

        assert item.description == "High quality beef"
        assert item.image_url == "http://example.com/burger.jpg"

    def test_menu_item_to_dict(self, app, sample_menu_item):
        """Test converting menu item to dictionary"""
        item_dict = sample_menu_item.to_dict()

        assert isinstance(item_dict, dict)
        assert item_dict["name"] == "Test Burger"
        assert item_dict["category"] == "patty"
        assert item_dict["price"] == 5.99
        assert "id" in item_dict
        assert "created_at" in item_dict

    def test_query_by_category(self, app, multiple_menu_items):
        """Test querying items by category"""
        patties = MenuItem.query.filter_by(category="patty").all()
        assert len(patties) == 2
        assert all(item.category == "patty" for item in patties)

    def test_query_available_items(self, app, multiple_menu_items):
        """Test querying only available items"""
        available = MenuItem.query.filter_by(is_available=True).all()
        assert len(available) == 4  # Turkey Patty is not available

    def test_query_healthy_choices(self, app, multiple_menu_items):
        """Test querying healthy choice items"""
        healthy = MenuItem.query.filter_by(is_healthy_choice=True).all()
        assert len(healthy) == 1
        assert healthy[0].name == "Lettuce"

    def test_update_menu_item(self, app, sample_menu_item):
        """Test updating menu item fields"""
        sample_menu_item.price = 6.99
        sample_menu_item.is_available = False
        db.session.commit()

        updated = MenuItem.query.get(sample_menu_item.id)
        assert float(updated.price) == 6.99
        assert updated.is_available is False

    def test_delete_menu_item(self, app, sample_menu_item):
        """Test deleting a menu item"""
        item_id = sample_menu_item.id
        db.session.delete(sample_menu_item)
        db.session.commit()

        deleted = MenuItem.query.get(item_id)
        assert deleted is None

    def test_timestamps(self, app):
        """Test that timestamps are set correctly"""
        item = MenuItem(name="Time Test", category="bun", price=1.00)
        db.session.add(item)
        db.session.commit()

        assert item.created_at is not None
        assert item.updated_at is not None
        assert item.created_at == item.updated_at
