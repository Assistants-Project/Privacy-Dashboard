from functools import wraps
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTExtendedException
from typing import Any

from flask import g, request
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClientError

from .exceptions import (
    ExpiredJWTException,
    InvalidJWTException,
    MissingJWTException,
    UserNotFoundException,
    WrongUserRoleException,
    UnloggedUserException,
)
from .extensions import jwt
from .models import User, UserRole
from .services import UserService

from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClientError, PyJWTError
from .integrations.smartotum.jwks import decode_smartotum_token
from .models import User, UserRole
from .repositories import UserRepository


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


def smartotum_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _ensure_smartotum_claims()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


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


def get_current_user_from_claims() -> User:
    claims = _ensure_smartotum_claims()

    current_user = getattr(g, "current_user", None)
    if current_user:
        return current_user

    user = UserRepository.get_user_by_uuid(UUID(claims["sub"]))
    if not user:
        raise UserNotFoundException("User not registered in Privacy Dashboard")

    g.current_user = user
    return user


def dc_or_dpo_required():
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

            raise WrongUserRoleException("User is not a Data Controller or DPO!")

        return decorator

    return wrapper



def ds_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):

            _ensure_smartotum_claims() #verify and 
            user = get_current_user_from_claims()
            user_role = user.role
            #if get_jwt()["role"] == UserRole.DATA_SUBJECT.value:
            if user_role == UserRole.DATA_SUBJECT:
                return fn(*args, **kwargs)

            raise WrongUserRoleException("User is not a Data Subject!")

        return decorator

    return wrapper


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
            if token and (_has_smartotum_session(token)):
                raise WrongUserRoleException("User already logged in!")
            if token and (_has_internal_session(token)):
                raise WrongUserRoleException("User already logged in!")
            return fn(*args, **kwargs)
        return decorator
    return wrapper

