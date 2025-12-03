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
        
        # Create OWL ontology for test user
        try:
            from app.services.owl_service import OWLService
            user_iri = OWLService.create_user_ontology(test_user.uuid)
            test_user.ontology_iri = user_iri
            db.session.commit()
        except Exception as e:
            print(f"Warning: Failed to create test user ontology: {e}")
    
    yield app
    
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def set_auth_cookie(app, client):
    """Set authentication cookie for test user"""
    from flask_jwt_extended import create_access_token
    from uuid import UUID as UUIDType
    
    with app.app_context():
        # Create token for the test user (ptp-demo)
        user_uuid = UUIDType("03af6091-280d-457f-a131-689449a144d8")
        access_token = create_access_token(identity=str(user_uuid), additional_claims={"role": "DATA_SUBJECT"})
        
        # Set the cookie in the test client
        client.set_cookie(
            domain='localhost',
            key='st_access_token',
            value=access_token,
            path='/'
        )
    
    return client
