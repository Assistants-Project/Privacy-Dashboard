import os
from datetime import timedelta


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
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_COOKIE_SECURE = True
    JWT_SESSION_COOKIE = False
    JWT_CSRF_METHODS = ["GET", "POST", "PUT", "DELETE"]


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI")
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
