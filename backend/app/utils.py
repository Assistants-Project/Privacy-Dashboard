from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any
from uuid import UUID

from flask import g, request
from flask_jwt_extended import (
    create_access_token,
    decode_token,
    get_jwt,
    set_access_cookies,
    verify_jwt_in_request,
)
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClientError, PyJWTError

from .error_handler import global_error_handler
from .exceptions import (
    ExpiredJWTException,
    InvalidJWTException,
    MissingJWTException,
    UnloggedUserException,
    UserNotFoundException,
    WrongUserRoleException,
)
from .extensions import jwt
from .integrations.smartotum.jwks import decode_smartotum_token
from .models import User, UserRole
from .repositories import UserRepository
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
def expired_token_callback(jwt_header, jwt_payload):
    return global_error_handler(
        ExpiredJWTException("The JSON Web Token has expired!")
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return global_error_handler(
        InvalidJWTException("The JSON Web Token is invalid!")
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return global_error_handler(
        MissingJWTException("The JSON Web Token is missing!")
    )

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


def _has_smartotum_session(token: str) -> bool:
    try:
        decode_smartotum_token(token)
        return True
    except (ExpiredSignatureError, InvalidTokenError, PyJWKClientError):
        return False


def _has_internal_session(token: str) -> bool:
    try:
        decode_token(token)
        return True
    except (JWTExtendedException, PyJWTError, RuntimeError, KeyError):
        return False


def _ensure_smartotum_claims() -> dict[str, Any]:
    """Ensure Smartotum claims are available for this request."""

    claims = getattr(g, "smartotum_claims", None)
    if claims is not None:
        return claims

    token = request.cookies.get("st_access_token")
    if not token:
        raise MissingJWTException("Smartotum access token missing")

    try:
        claims = decode_smartotum_token(token)
    except ExpiredSignatureError as exc:
        raise ExpiredJWTException("Smartotum token expired") from exc
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise InvalidJWTException("Smartotum token invalid") from exc

    g.smartotum_claims = claims
    return claims

#modular function that retrieves the information of the user
def get_current_user_from_claims() -> User:

    cached_user = getattr(g, "current_user", None)
    if cached_user:
        return cached_user

    token = request.cookies.get("st_access_token")
    if not token:
        raise MissingJWTException("Authentication token missing")

    if _has_internal_session(token):
        try:
            claims = decode_token(token)
            user_uuid = UUID(claims["sub"])
        except (JWTExtendedException, PyJWTError, RuntimeError, KeyError, ValueError) as exc:
            raise InvalidJWTException("The JSON Web Token is invalid!") from exc
    else:
        claims = _ensure_smartotum_claims()
        user_uuid = UUID(claims["sub"])

    user = UserRepository.get_user_by_uuid(user_uuid)
    if not user:
        raise UserNotFoundException("User not registered in Privacy Dashboard")

    g.current_user = user
    return user


#for now not used
def smartotum_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _ensure_smartotum_claims()
            return fn(*args, **kwargs)

        return decorator

    return wrapper

def dc_or_dpo_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user_from_claims()
            if user.role in (
                UserRole.DATA_CONTROLLER,
                UserRole.DATA_PROTECTION_OFFICER,
            ):
                return fn(*args, **kwargs, current_user=user)

            raise WrongUserRoleException("User is not a Data Controller or DPO!")

        return decorator

    return wrapper


def ds_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user_from_claims()
            if user.role == UserRole.DATA_SUBJECT:
                return fn(*args, **kwargs, current_user=user)

            raise WrongUserRoleException("User is not a Data Subject!")

        return decorator

    return wrapper


#simple, used for logout
def logged_in_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            token = request.cookies.get("st_access_token")
            if not token:
                raise UnloggedUserException("User not logged in!")

            if _has_smartotum_session(token) or _has_internal_session(token):
                return fn(*args, **kwargs)

            raise UnloggedUserException("User not logged in!")

        return decorator

    return wrapper


def unlogged_required():
    """Decorator that ensures the user making the request is not logged in. If the
    user is already logged in, it raises a 403 Forbidden error. This decorator
    verifies the JWT (DATA_CONTROLLER,DPO) or Smartotum (DATA_SUBJECT) token in the request and checks whether the user is already logged in before
    allowing access to the decorated function.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            token = request.cookies.get("st_access_token")
            if token and (_has_smartotum_session(token) or _has_internal_session(token)):
                raise WrongUserRoleException("User already logged in!")
            return fn(*args, **kwargs)

        return decorator

    return wrapper
