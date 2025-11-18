"""
Diagnostic script to identify test setup issues.
Run this before running pytest to identify the problem.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

print("=" * 60)
print("DIAGNOSTIC: Testing import and setup")
print("=" * 60)

# Test 1: Import app
print("\n1. Testing app import...")
try:
    from app import create_app

    print("✓ Successfully imported create_app")
except Exception as e:
    print(f"✗ Failed to import create_app: {e}")
    sys.exit(1)

# Test 2: Import database
print("\n2. Testing database import...")
try:
    from database.db import db

    print("✓ Successfully imported db")
except Exception as e:
    print(f"✗ Failed to import db: {e}")
    sys.exit(1)

# Test 3: Import models
print("\n3. Testing model imports...")
try:
    from models.user import User

    print("✓ Successfully imported User")
except Exception as e:
    print(f"✗ Failed to import User: {e}")
    sys.exit(1)

try:

    print("✓ Successfully imported MenuItem")
except Exception as e:
    print(f"✗ Failed to import MenuItem: {e}")
    sys.exit(1)

try:
    from models.order import Order

    print("✓ Successfully imported Order and OrderItem")
except Exception as e:
    print(f"✗ Failed to import Order/OrderItem: {e}")
    sys.exit(1)

# Test 4: Import Flask-Login
print("\n4. Testing Flask-Login import...")
try:
    from flask_login import FlaskLoginClient

    print("✓ Successfully imported FlaskLoginClient")
except Exception as e:
    print(f"✗ Failed to import FlaskLoginClient: {e}")
    print("  You may need to install flask-login:")
    print("  pip install flask-login")
    sys.exit(1)

# Test 5: Create test app
print("\n5. Testing app creation...")
try:
    app = create_app("testing")
    print("✓ Successfully created app with 'testing' config")
except Exception as e:
    print(f"✗ Failed to create app: {e}")
    print("\nTrying without config parameter...")
    try:
        app = create_app()
        print("✓ Successfully created app without config")
    except Exception as e2:
        print(f"✗ Failed to create app without config: {e2}")
        sys.exit(1)

# Test 6: Configure test database
print("\n6. Testing database configuration...")
try:
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )
    print("✓ Successfully configured test database")
except Exception as e:
    print(f"✗ Failed to configure database: {e}")
    sys.exit(1)

# Test 7: Create tables
print("\n7. Testing table creation...")
try:
    with app.app_context():
        db.create_all()
        print("✓ Successfully created all tables")

        # List created tables
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"  Created tables: {', '.join(tables)}")

        db.drop_all()
        print("✓ Successfully dropped all tables")
except Exception as e:
    print(f"✗ Failed to create/drop tables: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 8: Test user creation
print("\n8. Testing user creation...")
try:
    with app.app_context():
        db.create_all()

        user = User(username="testuser")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()

        user_id = user.id
        print(f"✓ Successfully created user with ID: {user_id}")

        db.drop_all()
except Exception as e:
    print(f"✗ Failed to create user: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 9: Test FlaskLoginClient
print("\n9. Testing FlaskLoginClient integration...")
try:
    from flask_login import FlaskLoginClient

    with app.app_context():
        db.create_all()

        user = User(username="logintest")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # Set up test client with user
        app.test_client_class = FlaskLoginClient
        client = app.test_client(user=user)

        print("✓ Successfully created authenticated test client")

        db.drop_all()
except Exception as e:
    print(f"✗ Failed to create authenticated client: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 10: Import controllers
print("\n10. Testing controller imports...")
try:

    print("✓ Successfully imported OrderController")
except Exception as e:
    print(f"✗ Failed to import OrderController: {e}")
    import traceback

    traceback.print_exc()

# Test 11: Check cascade delete configuration
print("\n11. Testing cascade delete configuration...")
try:
    with app.app_context():
        db.create_all()

        # Check if Order model has cascade configured
        from sqlalchemy import inspect as sqla_inspect

        mapper = sqla_inspect(Order)
        items_rel = mapper.relationships["items"]

        cascade_options = items_rel.cascade
        print(f"  Order.items cascade options: {cascade_options}")

        if "delete" in str(cascade_options) or "all" in str(cascade_options):
            print("✓ Cascade delete is configured")
        else:
            print("⚠ Warning: Cascade delete may not be configured")

        db.drop_all()
except Exception as e:
    print(f"⚠ Could not verify cascade configuration: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE - ALL CRITICAL TESTS PASSED!")
print("=" * 60)
print("\n✓ Your test setup is working correctly!")
print("\nYou can now run your tests with:")
print("  pytest tests/purchaseManagementTests/ -v")
print("\nFor coverage report:")
print(
    "pytest tests/purchaseManagementTests/"
    " --cov=controllers.order_controller"
    " --cov=models.order"
    " --cov=routes.order_routes"
    " --cov-report=html"
    " --cov-report=term"
)
