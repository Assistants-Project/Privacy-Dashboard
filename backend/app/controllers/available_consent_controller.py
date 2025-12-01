from typing import List
from uuid import UUID

from flask_smorest import Blueprint

from ..exceptions import (
    AvailableConsentEmptyListException,
    AvailableConsentWrongListException,
)
from ..schemas import (
    ApplicationUuidReqSchema,
    AvailableConsentResSchema,
    AvailableConsentsReqSchema,
    SmartHomeUuidReqSchema,
)
from ..services import AvailableConsentService
from ..utils import ds_required, logged_in_required

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
