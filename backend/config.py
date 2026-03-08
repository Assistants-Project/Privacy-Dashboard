import os
from datetime import timedelta


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "30e10900abeadf6f02b786f6f1bcf30a")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TITLE = "Privacy Dashboard API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.1.1"
    OPENAPI_URL_PREFIX = "/docs"
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "3301947240a7448b5c90462c7d981d10")
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_ACCESS_COOKIE_NAME = "st_access_token"
    JWT_COOKIE_CSRF_PROTECT = _env_bool("JWT_COOKIE_CSRF_PROTECT", True)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_COOKIE_SECURE = _env_bool("JWT_COOKIE_SECURE", True)
    JWT_SESSION_COOKIE = False
    JWT_CSRF_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    # --- Smartotum ---
    SMARTOTUM_BASE_URL = os.getenv("SMARTOTUM_BASE_URL", "https://api.smartotum.com")
    SMARTOTUM_DHT_URL = os.getenv("SMARTOTUM_DHT_URL", "https://house_name.pods.smartotum.com/.dht/")
    SMARTOTUM_API_BASE_PATH = os.getenv("SMARTOTUM_API_BASE_PATH", "/auth")
    SMARTOTUM_AUTH_MODE = os.getenv("SMARTOTUM_AUTH_MODE", "header")
    SMARTOTUM_RID = os.getenv("SMARTOTUM_RID", "emailpassword")
    SMARTOTUM_DEVICE_TOPICS = [
        t.strip()
        for t in os.getenv(
            "SMARTOTUM_DEVICE_TOPICS",
            "domo_light,domo_light_dimmable,domo_rgbw_light,domo_switch,domo_roller_shutter,domo_camera",
        ).split(",")
        if t.strip()
    ]
    SMARTOTUM_RULE_TOPIC = os.getenv("SMARTOTUM_RULE_TOPIC", "privacy_rule")
    SMARTOTUM_JWKS_URL = os.getenv("SMARTOTUM_JWKS_URL","https://api.smartotum.com/auth/jwt/jwks.json")
    SMARTOTUM_ISSUER = os.getenv("SMARTOTUM_ISSUER", "https://api.smartotum.com/auth")
    SMARTOTUM_TIMEOUT = float(os.getenv("SMARTOTUM_TIMEOUT", "5")) #max time a http request to smartotum api can last

    # --- Ontology ---
    ONTOLOGY_DIRECTORY = os.getenv("ONTOLOGY_DIRECTORY", "app/ontologies/")
    ONTOLOGY_SIFIS_FILE = os.getenv("ONTOLOGY_SIFIS_FILE", "sifis-home.owl")

    # --- Logging ---
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

    # If set, Smartotum applications are loaded from this local JSON file instead of calling the remote API.
    SMARTOTUM_APPLICATIONS_JSON = os.getenv("SMARTOTUM_APPLICATIONS_JSON", None)
    # If set, Marketplace applications are loaded from this local JSON file (mock) instead of calling a remote API.
    MARKETPLACE_APPLICATIONS_JSON = os.getenv("MARKETPLACE_APPLICATIONS_JSON", None)
    # Token used by external marketplace to call integration endpoints.
    MARKETPLACE_INTEGRATION_TOKEN = os.getenv("MARKETPLACE_INTEGRATION_TOKEN", None)

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")
    # SQLALCHEMY_ECHO = True  # Commented out to reduce log verbosity


class DemoConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEMO_DATABASE_URI")
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")


config_by_name = {
    "development": DevelopmentConfig,
    "demo": DemoConfig,
    "testing": TestingConfig,
}
