from functools import wraps
from typing import Any
from uuid import UUID

from flask import g, request
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClientError

from .exceptions import (
    ExpiredJWTException,
    InvalidJWTException,
    MissingJWTException,
    UserNotFoundException,
    WrongUserRoleException,
)
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
            user = get_current_user_from_claims()
            if user.role in (
                UserRole.DATA_CONTROLLER,
                UserRole.DATA_PROTECTION_OFFICER,
            ):
                return fn(*args, **kwargs)

            raise WrongUserRoleException("User is not a Data Controller or DPO!")

        return decorator

    return wrapper


def ds_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user_from_claims()
            if user.role == UserRole.DATA_SUBJECT:
                return fn(*args, **kwargs)

            raise WrongUserRoleException("User is not a Data Subject!")

        return decorator

    return wrapper


def unlogged_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                _ensure_smartotum_claims()
            except (MissingJWTException, InvalidJWTException, ExpiredJWTException):
                return fn(*args, **kwargs)

            raise WrongUserRoleException("User already logged in!")

        return decorator

    return wrapper

