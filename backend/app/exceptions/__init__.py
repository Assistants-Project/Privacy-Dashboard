from .auth_exceptions import (
    ExpiredJWTException,
    InvalidJWTException,
    MissingJWTException,
)
from .entities.application_exceptions import ApplicationNotFoundException
from .entities.available_consent_exceptions import (
    AvailableConsentApplicationMismatchException,
    AvailableConsentEmptyListException,
    AvailableConsentNotFoundException,
    AvailableConsentWrongListException,
)
from .entities.device_exceptions import DeviceSyncException
from .entities.home_exception import (
    SmartHomeForbiddenException,
    SmartHomeNotFoundException,
)
from .entities.privacy_notice_exceptions import PrivacyNoticeNotFoundException
from .entities.request_exceptions import RequestNotFoundException
from .entities.room_exceptions import RoomNotFoundException, RoomSyncException
from .entities.smartotum_exceptions import SmartotumSyncException
from .entities.user_exceptions import (
    UnloggedUserException,
    UserAlreadyRegisteredException,
    UserNotFoundException,
    WrongUserCredentialsException,
    WrongUserRoleException,
    WrongUserUuidException,
)
from .relations.user_smart_home_available_consent_exceptions import (
    UserSmartHomeAvailableConsentAlreadyCreatedException,
    UserSmartHomeAvailableConsentCreationException,
)

__all__ = [
    "ExpiredJWTException",
    "InvalidJWTException",
    "MissingJWTException",
    "ApplicationNotFoundException",
    "AvailableConsentApplicationMismatchException",
    "AvailableConsentEmptyListException",
    "AvailableConsentNotFoundException",
    "AvailableConsentWrongListException",
    "PrivacyNoticeNotFoundException",
    "RequestNotFoundException",
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
    "UserSmartHomeAvailableConsentAlreadyCreatedException",
    "UserSmartHomeAvailableConsentCreationException",
]
