from .auth_exceptions import (
    ExpiredJWTException,
    InvalidJWTException,
    MissingJWTException,
)
from .entities.application_exceptions import ApplicationNotFoundException
from .entities.privacy_notice_exceptions import PrivacyNoticeNotFoundException
from .entities.user_exceptions import (
    UserNotFoundException,
    WrongUserCredentialsException,
    WrongUserRoleException,
    WrongUserUuidException,
    UnloggedUserException,
    UserAlreadyRegisteredException,
)

__all__ = [
    "ExpiredJWTException",
    "InvalidJWTException",
    "MissingJWTException",
    "ApplicationNotFoundException",
    "PrivacyNoticeNotFoundException",
    "UserNotFoundException",
    "WrongUserCredentialsException",
    "WrongUserRoleException",
    "WrongUserUuidException",
    "UnloggedUserException",
    "UserAlreadyRegisteredException",
]
