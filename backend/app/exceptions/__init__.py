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
from .entities.room_exceptions import RoomNotFoundException, RoomSyncException
from .entities.home_exception import SmartHomeNotFoundException
from .entities.home_exception import SmartHomeForbiddenException
from .entities.device_exceptions import DeviceSyncException
from .entities.smartotum_exceptions import (
    SmartotumSyncException,
    SmartotumServiceUnavailableException,
    SmartotumTimeoutException,
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
    "RoomNotFoundException",
    "RoomSyncException",
    "SmartHomeNotFoundException",
    "SmartHomeForbiddenException",
    "DeviceSyncException",
    "SmartotumSyncException",
    "SmartotumServiceUnavailableException",
    "SmartotumTimeoutException",

]
