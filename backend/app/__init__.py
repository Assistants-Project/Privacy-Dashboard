import os
from pathlib import Path
from typing import Optional

from config import config_by_name
from flask import Flask, abort, send_from_directory
from flask_cors import CORS

from .controllers import (
    application_bp,
    auth_bp,
    available_consent_bp,
    homes_bp,
    message_bp,
    privacy_notice_bp,
    question_bp,
    request_bp,
    sifis_bp,
    user_bp,
)
from .error_handler import global_error_handler
from .extensions import api, db, jwt, ma, migrate
from .initial_data import (
    init_data,
    load_pia_schema,
    load_pia_template,
    load_privacy_notice_template,
)
from .utils import refresh_expiring_jwts


def create_app(env_name: Optional[str] = None) -> Flask:
    """
    Creates and configures the Flask app instance.
    Assumes Flask CLI has already auto-loaded .env for development.
    """
    env_name = env_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[env_name])
    app.config.setdefault("JSON_SORT_KEYS", False)

    allowed_origins = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if o.strip()
    ]
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Disposition"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    api.init_app(app)
    jwt.init_app(app)

    for blueprint in [
        application_bp,
        auth_bp,
        available_consent_bp,
        homes_bp,
        message_bp,
        privacy_notice_bp,
        question_bp,
        request_bp,
        user_bp,
        sifis_bp,
    ]:
        api.register_blueprint(blueprint)

    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.exists():

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path: str):
            if path.startswith("api") or path.startswith("docs"):
                abort(404)

            asset_path = frontend_dist / path
            if path and asset_path.exists() and asset_path.is_file():
                return send_from_directory(frontend_dist, path)

            return send_from_directory(frontend_dist, "index.html")

    app.after_request(refresh_expiring_jwts)
    app.register_error_handler(Exception, global_error_handler)

    # Add dummy initial data in development and demo mode
    if env_name in {"development", "demo"}:
        init_data(app)

    from .commands import generate_owls_command

    app.cli.add_command(generate_owls_command)

    # Load template of Privacy Notice
    load_privacy_notice_template()

    # Load template of Privacy Impact Assessment
    load_pia_template()

    # Load JSON Schema to validate incoming Privacy Impact Assessments
    load_pia_schema()

    return app
