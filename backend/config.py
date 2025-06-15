import os

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', '30e10900abeadf6f02b786f6f1bcf30a')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI')

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI')
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

config_by_name = {
    'development': DevelopmentConfig,
    'testing':     TestingConfig,
    'production':  ProductionConfig,
}