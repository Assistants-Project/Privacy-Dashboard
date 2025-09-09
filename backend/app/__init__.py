import os
from pathlib import Path

from config import config_by_name
from dotenv import load_dotenv
from flask import Flask

from .controllers import application_bp, auth_bp, message_bp, privacy_notice_bp, user_bp
from .error_handler import global_error_handler
from .extensions import api, db, jwt, ma, migrate
from .initial_data import init_data
from .utils import refresh_expiring_jwts


def create_app(env_name: str = None) -> Flask:
    """
    Creates and configures the Flask app instance.
    Assumes Flask CLI has already auto-loaded .env for development.
    """

    env_name = env_name or os.getenv("FLASK_ENV", "development")

    override_map = {"testing": ".env.test", "production": ".env.prod"}
    override_file = override_map.get(env_name)
    if override_file:
        path = Path("../" + override_file)
        if path.exists():
            load_dotenv(path, override=True)
        else:
            print(f"[WARNING] Override env file not found: {override_file}")

    app = Flask(__name__)
    app.config.from_object(config_by_name[env_name])

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    api.init_app(app)
    jwt.init_app(app)

    for blueprint in [application_bp, auth_bp, message_bp, privacy_notice_bp, user_bp]:
        app.register_blueprint(blueprint)

    app.after_request(refresh_expiring_jwts)

    app.register_error_handler(Exception, global_error_handler)

    # Add dummy initial data only in development
    if env_name == "development":
        init_data(app)

    return app
