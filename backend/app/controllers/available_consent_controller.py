from uuid import UUID

from flask_smorest import Blueprint

from ..schemas import ApplicationUuidReqSchema, AvailableConsentResSchema
from ..services import AvailableConsentService
from ..utils import logged_in_required

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
