from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    set_access_cookies,
    verify_jwt_in_request,
)
from flask_jwt_extended.exceptions import NoAuthorizationError

from .error_handler import global_error_handler
from .exceptions import (
    ExpiredJWTException,
    InvalidJWTException,
    MissingJWTException,
    UserNotFoundException,
    WrongUserRoleException,
)
from .extensions import jwt
from .models import User, UserRole
from .services import UserService


# https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    try:
        return UserService.get_user_by_uuid(jwt_data["sub"])
    except UserNotFoundException:
        return None


# https://flask-jwt-extended.readthedocs.io/en/stable/changing_default_behavior.html
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return global_error_handler(ExpiredJWTException("The JSON Web Token has expired!"))


@jwt.invalid_token_loader
def my_invalid_token_callback(error):
    return global_error_handler(InvalidJWTException("The JSON Web Token is invalid!"))


@jwt.unauthorized_loader
def my_missing_token_callback(error):
    return global_error_handler(MissingJWTException("The JSON Web Token is missing!"))


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
def dc_or_dpo_required():
    """Decorator that ensures the user making the request has a role of
    `DATA_CONTROLLER` or `DATA_PROTECTION_OFFICER`. If the user's role is
    neither of these, it returns a 403 Forbidden error. This decorator
    verifies the JWT in the request and checks the user's role before
    allowing access to the decorated function.
    """

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
                raise WrongUserRoleException("User is not a Data Controller or DPO!")

        return decorator

    return wrapper


def ds_required():
    """Decorator that ensures the user making the request has a role of
    `DATA_SUBJECT`. If the user's role is not data subject, it returns
    a 403 Forbidden error. This decorator verifies the JWT in the
    request and checks the user's role before allowing access to
    the decorated function.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt()["role"] == UserRole.DATA_SUBJECT.value:
                return fn(*args, **kwargs)
            else:
                raise WrongUserRoleException("User is not a Data Subject!")

        return decorator

    return wrapper


def unlogged_required():
    """Decorator that ensures the user making the request is not logged in. If the
    user is already logged in, it raises a 403 Forbidden error. This decorator
    verifies the JWT in the request and checks whether the user is already logged in before
    allowing access to the decorated function.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                raise WrongUserRoleException("User already logged in!")
            except NoAuthorizationError:
                return fn(*args, **kwargs)

        return decorator

    return wrapper
