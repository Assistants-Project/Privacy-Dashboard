import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from config import config_by_name
from .extensions import db, migrate, api
from .controllers import testObj_bp

def create_app(env_name: str = None) -> Flask:
    """
    Creates and configures the Flask app instance.
    Assumes Flask CLI has already auto-loaded .env for development.
    """

    env_name = env_name or os.getenv("FLASK_ENV", "development")

    override_map = {
        "testing":    ".env.test",
        "production": ".env.prod"
    }
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
    api.init_app(app)

    api.register_blueprint(testObj_bp)

    return app
