from .request.application_and_privacy_notice_uuid_req_schema import (
    ApplicationAndPrivacyNoticeUuidReqSchema,
)
from .request.application_and_available_consent_uuid_req_schema import (
    ApplicationAndAvailableConsentUuidReqSchema,
)
from .request.application_and_user_email_req_schema import (
    ApplicationAndUserEmailReqSchema,
)
from .request.application_and_user_uuid_req_schema import (
    ApplicationAndUserUuidReqSchema,
)
from .request.application_create_req_schema import ApplicationCreateReqSchema
from .request.application_patch_req_schema import ApplicationPatchReqSchema
from .request.application_uuid_req_schema import ApplicationUuidReqSchema
from .request.optional_application_uuid_req_schema import OptionalApplicationUuidReqSchema
from .request.auth_req_schema import AuthReqSchema
from .request.current_user_patch_req_schema import CurrentUserPatchReqSchema
from .request.available_consent_content_req_schema import AvailableConsentContentReqSchema
from .request.available_consents_req_schema import AvailableConsentsReqSchema
from .request.message_req_schema import MessageReqSchema
from .request.marketplace_application_register_req_schema import (
    MarketplaceApplicationRegisterReqSchema,
)
from .request.marketplace_application_patch_req_schema import (
    MarketplaceApplicationPatchReqSchema,
)
from .request.privacy_impact_assessment_req_schema import PrivacyImpactAssessmentReqSchema
from .request.privacy_notice_req_schema import PrivacyNoticeReqSchema
from .request.questionnaire_req_schema import QuestionnaireReqSchema
from .request.registration_req_schema import RegistrationReqSchema
from .request.request_handling_req_schema import RequestHandlingReqSchema
from .request.request_req_schema import RequestReqSchema
from .request.request_status_req_schema import RequestStatusReqSchema
from .request.request_uuid_req_schema import RequestUuidReqSchema
from .request.smart_home_uuid_req_schema import SmartHomeUuidReqSchema
from .request.smart_home_and_application_uuid_req_schema import (
    SmartHomeAndApplicationUuidReqSchema,
)
from .request.user_role_req_schema import UserRoleReqSchema
from .request.user_uuid_req_schema import UserUuidReqSchema
from .response.application_res_schema import (
    InstalledApplicationResSchema,
    ManagedApplicationResSchema,
)
from .response.available_consent_res_schema import (
    ConsentStateResSchema,
    AvailableConsentResSchema,
)
from .response.device_res_schema import DeviceResSchema
from .response.home_res_schema import HomeResSchema
from .response.message_res_schema import MessageResSchema
from .response.privacy_impact_assessment_res_schema import PrivacyImpactAssessmentResSchema
from .response.privacy_notice_res_schema import PrivacyNoticeResSchema
from .response.question_res_schema import QuestionResSchema
from .response.questionnaire_res_schema import QuestionnaireResSchema
from .response.refresh_result_res_schema import RefreshResultResSchema
from .response.request_res_schema import RequestResSchema, RequestSchema
from .response.room_res_schema import RoomResSchema
from .response.user_message_res_schema import UserMessageResSchema
from .response.user_res_schema import UserResSchema

__all__ = [
    "ApplicationAndPrivacyNoticeUuidReqSchema",
    "ApplicationAndAvailableConsentUuidReqSchema",
    "ApplicationAndUserEmailReqSchema",
    "ApplicationAndUserUuidReqSchema",
    "ApplicationCreateReqSchema",
    "ApplicationPatchReqSchema",
    "ApplicationUuidReqSchema",
    "OptionalApplicationUuidReqSchema",
    "AuthReqSchema",
    "CurrentUserPatchReqSchema",
    "AvailableConsentContentReqSchema",
    "AvailableConsentsReqSchema",
    "MessageReqSchema",
    "MarketplaceApplicationPatchReqSchema",
    "MarketplaceApplicationRegisterReqSchema",
    "PrivacyImpactAssessmentReqSchema",
    "PrivacyNoticeReqSchema",
    "QuestionnaireReqSchema",
    "RegistrationReqSchema",
    "RequestHandlingReqSchema",
    "RequestReqSchema",
    "RequestStatusReqSchema",
    "RequestUuidReqSchema",
    "SmartHomeUuidReqSchema",
    "SmartHomeAndApplicationUuidReqSchema",
    "UserRoleReqSchema",
    "UserUuidReqSchema",
    "ConsentStateResSchema",
    "ManagedApplicationResSchema",
    "AvailableConsentResSchema",
    "DeviceResSchema",
    "HomeResSchema",
    "MessageResSchema",
    "PrivacyImpactAssessmentResSchema",
    "PrivacyNoticeResSchema",
    "QuestionResSchema",
    "QuestionnaireResSchema",
    "RefreshResultResSchema",
    "RequestResSchema",
    "RequestSchema",
    "RoomResSchema",
    "UserMessageResSchema",
    "UserResSchema",
    "InstalledApplicationResSchema",
]
