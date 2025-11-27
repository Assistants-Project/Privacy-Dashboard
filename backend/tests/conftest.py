# Test configuration and fixtures
import pytest
import sys
import os
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

os.environ["FLASK_ENV"] = "development"  # Use development config
os.environ["DEV_DATABASE_URI"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["SECRET_KEY"] = "test-secret"

from app import create_app
from app.extensions import db
from app.models.entities.user import User, UserRole


@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    # Create app with development config (which now uses memory SQLite from env)
    app = create_app()
    
    # Override config
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
    })
    
    with app.app_context():
        db.create_all()
        
        # Create test user with hashed password
        from werkzeug.security import generate_password_hash
        from uuid import UUID as UUIDType
        
        test_user = User(
            uuid=UUIDType("03af6091-280d-457f-a131-689449a144d8"),
            firstname="Test",
            lastname="User",
            email="ptp-demo",
            role=UserRole.DATA_SUBJECT,
            password_hash=generate_password_hash("test-password")
        )
        db.session.add(test_user)
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def auth_headers():
    """Get authorization headers for test user"""
    import base64
    credentials = base64.b64encode(b"ptp-demo:test-password").decode("utf-8")
    return {"Authorization": f"Basic {credentials}"}
