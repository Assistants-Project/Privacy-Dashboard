from .application_controller import application_bp
from .auth_controller import auth_bp
from .privacy_notice_controller import privacy_notice_bp
from .user_controller import user_bp

__all__ = ["auth_bp", "application_bp", "privacy_notice_bp", "user_bp"]
