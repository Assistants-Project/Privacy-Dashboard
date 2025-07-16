from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    set_access_cookies,
    verify_jwt_in_request,
)

from .extensions import jwt
from .models import User, UserRole
from .services import UserService


# https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    try:
        return UserService.find_user_by_email(jwt_data["sub"])
    except Exception:
        return None


# https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens.html#implicit-refreshing-with-cookies
def refresh_expiring_jwts(response):
    # Skip refresh for login and logout endpoint
    if (
        request.endpoint == "Authentication API.login"
        or request.endpoint == "Authentication API.logout"
    ):
        return response
    try:
        old_jwt = get_jwt()
        exp_timestamp = old_jwt["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(
                identity=old_jwt["sub"], additional_claims={"role": old_jwt["role"]}
            )
            set_access_cookies(response, access_token)
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        pass
    return response


# https://flask-jwt-extended.readthedocs.io/en/stable/custom_decorators.html
def data_controller_or_dpo_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_role = get_jwt()["role"]
            if (
                user_role == UserRole.DATA_CONTROLLER.value
                or user_role == UserRole.DATA_PROTECTION_OFFICER.value
            ):
                return fn(*args, **kwargs)
            else:
                return {
                    "code": 403,
                    "message": "User is not a data controller or dpo",
                    "status": "Forbidden",
                }, 403

        return decorator

    return wrapper


def data_subject_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt()["role"] == UserRole.DATA_SUBJECT.value:
                return fn(*args, **kwargs)
            else:
                return {
                    "code": 403,
                    "message": "User is not a data subject",
                    "status": "Forbidden",
                }, 403

        return decorator

    return wrapper


def unlogged_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return {
                    "code": 403,
                    "message": "User already logged in",
                    "status": "Forbidden",
                }, 403
            except Exception:
                return fn(*args, **kwargs)

        return decorator

    return wrapper
