from .auth_exceptions import (
    ExpiredJWTException,
    InvalidJWTException,
    MissingJWTException,
)
from .entities.application_exceptions import (
    ApplicationAlreadyAssignedException,
    ApplicationAlreadyExistsException,
    ApplicationNotFoundException,
    ApplicationNotManagedException,
    DpoAlreadyAssignedException,
    InvalidApplicationNameException,
    InvalidPrivacyImpactAssessmentException,
    MissingDpoUuidException,
    MissingPrivacyImpactAssessmentException,
    MissingTemplateException,
    MissingValidationSchemaException,
    PrivacyImpactAssessmentNotFoundException,
)
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
from .entities.privacy_notice_exceptions import (
    PrivacyNoticeAlreadyExists,
    PrivacyNoticeNotFoundException,
)
from .entities.question_exceptions import (
    InvalidAnswerContentException,
    MissingRequiredAnswerException,
    QuestionNotFoundException,
)
from .entities.request_exceptions import RequestNotFoundException
from .entities.room_exceptions import RoomNotFoundException, RoomSyncException
from .entities.smartotum_exceptions import (
    SmartotumServiceUnavailableException,
    SmartotumSyncException,
    SmartotumTimeoutException,
)
from .entities.user_exceptions import (
    UnloggedUserException,
    UserAlreadyRegisteredException,
    UserNotFoundException,
    WrongUserCredentialsException,
    WrongUserRoleException,
    WrongUserUuidException,
)
from .entities.user_profile_exceptions import UserEmailAlreadyInUseException
from .relations.question_application_exceptions import (
    QuestionnaireNotFoundException,
    QuestionnaireSubmissionException,
)
from .relations.user_smart_home_available_consent_exceptions import (
    UserSmartHomeAvailableConsentAlreadyCreatedException,
    UserSmartHomeAvailableConsentCreationException,
    UserSmartHomeAvailableConsentDeletionException,
)

__all__ = [
    "ExpiredJWTException",
    "InvalidJWTException",
    "MissingJWTException",
    "ApplicationAlreadyExistsException",
    "ApplicationAlreadyAssignedException",
    "ApplicationNotFoundException",
    "ApplicationNotManagedException",
    "DpoAlreadyAssignedException",
    "InvalidApplicationNameException",
    "InvalidPrivacyImpactAssessmentException",
    "MissingDpoUuidException",
    "MissingPrivacyImpactAssessmentException",
    "MissingTemplateException",
    "MissingValidationSchemaException",
    "PrivacyImpactAssessmentNotFoundException",
    "AvailableConsentApplicationMismatchException",
    "AvailableConsentEmptyListException",
    "AvailableConsentNotFoundException",
    "AvailableConsentWrongListException",
    "PrivacyNoticeAlreadyExists",
    "PrivacyNoticeNotFoundException",
    "InvalidAnswerContentException",
    "MissingRequiredAnswerException",
    "QuestionNotFoundException",
    "RequestNotFoundException",
    "UserEmailAlreadyInUseException",
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
    "QuestionnaireNotFoundException",
    "QuestionnaireSubmissionException",
    "UserSmartHomeAvailableConsentAlreadyCreatedException",
    "UserSmartHomeAvailableConsentCreationException",
    "UserSmartHomeAvailableConsentDeletionException",
    "SmartotumServiceUnavailableException",
    "SmartotumTimeoutException",
]
