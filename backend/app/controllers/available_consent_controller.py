from typing import List
from uuid import UUID

from flask_smorest import Blueprint

from ..exceptions import (
    AvailableConsentEmptyListException,
    AvailableConsentWrongListException,
)
from ..schemas import (
    ApplicationUuidReqSchema,
    AvailableConsentGivenResSchema,
    AvailableConsentResSchema,
    AvailableConsentsReqSchema,
    SmartHomeUuidReqSchema,
    UserAndSmartHomeAndApplicationUuidReqSchema,
    UserAndSmartHomeAndAvailableConsentUuidReqSchema,
)
from ..services import AvailableConsentService
from ..utils import dc_or_dpo_required, ds_required, logged_in_required

available_consent_bp = Blueprint(
    "Available Consents API",
    "available_consent_bp",
    url_prefix="/api/available-consents",
    description="Endpoints for available consents",
)


@available_consent_bp.route("/application/<application_uuid>", methods=["GET"])
@available_consent_bp.arguments(
    ApplicationUuidReqSchema, location="path", as_kwargs=True
)
@available_consent_bp.response(200, AvailableConsentResSchema(many=True))
@logged_in_required()
def get_available_consents_by_application_uuid(application_uuid: UUID, current_user):
    return AvailableConsentService.get_available_consents_by_application_uuid(
        current_user.id, application_uuid
    )


@available_consent_bp.route("/home/<smart_home_uuid>", methods=["GET"])
@available_consent_bp.arguments(SmartHomeUuidReqSchema, location="path", as_kwargs=True)
@available_consent_bp.response(200, AvailableConsentGivenResSchema(many=True))
@ds_required()
def get_given_consents_by_smart_home_uuid(smart_home_uuid: str, current_user):
    return AvailableConsentService.get_given_consents_by_ds_id_and_smart_home_uuid(
        current_user.id, smart_home_uuid
    )


@available_consent_bp.route("/home/<smart_home_uuid>", methods=["POST"])
@available_consent_bp.arguments(SmartHomeUuidReqSchema, location="path", as_kwargs=True)
@available_consent_bp.arguments(
    AvailableConsentsReqSchema, location="json", as_kwargs=True
)
@ds_required()
def give_consents_in_smart_home(
    smart_home_uuid: str, selected_consents: List[UUID], current_user
):
    if not selected_consents:
        raise AvailableConsentEmptyListException("No consents selected!")
    if len(selected_consents) != len(set(selected_consents)):
        raise AvailableConsentWrongListException("Duplicate consents selected!")
    AvailableConsentService.give_consents_in_smart_home(
        current_user.id, smart_home_uuid, selected_consents
    )
    return "", 204


@available_consent_bp.route("/given-consent", methods=["DELETE"])
@available_consent_bp.arguments(
    UserAndSmartHomeAndAvailableConsentUuidReqSchema, location="json", as_kwargs=True
)
@dc_or_dpo_required()
def delete_given_consent_by_ds_uuid_and_smart_home_uuid_and_available_consent_uuid(
    user_uuid: UUID, smart_home_uuid: str, available_consent_uuid: UUID, current_user
):
    AvailableConsentService.delete_given_consent_by_ds_uuid_and_smart_home_uuid_and_available_consent_uuid(
        current_user.id, user_uuid, smart_home_uuid, available_consent_uuid
    )
    return "", 204


@available_consent_bp.route("/given-consents/application", methods=["DELETE"])
@available_consent_bp.arguments(
    UserAndSmartHomeAndApplicationUuidReqSchema, location="json", as_kwargs=True
)
@dc_or_dpo_required()
def delete_given_consent_by_ds_uuid_and_smart_home_uuid_and_application_uuid(
    user_uuid: UUID, smart_home_uuid: str, application_uuid: UUID, current_user
):
    AvailableConsentService.delete_given_consent_by_ds_uuid_and_smart_home_uuid_and_application_uuid(
        current_user.id, user_uuid, smart_home_uuid, application_uuid
    )
    return "", 204
