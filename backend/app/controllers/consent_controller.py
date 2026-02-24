from uuid import UUID
from flask_smorest import Blueprint
from ..schemas import (ApplicationAndAvailableConsentUuidReqSchema,ApplicationUuidReqSchema,AvailableConsentContentReqSchema,AvailableConsentResSchema,AvailableConsentsReqSchema,ConsentStateResSchema,SmartHomeAndApplicationUuidReqSchema)
from ..services import ConsentService
from ..utils import dc_or_dpo_required, ds_required, logged_in_required

consent_bp = Blueprint(
    "Consents API",
    "consent_bp",
    url_prefix="/api/consents",
    description="Endpoints for consent catalog and consent state",
)

# ritorna tutti i consensi disponibili per app
@consent_bp.route("/application/<application_uuid>", methods=["GET"])
@consent_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@consent_bp.response(200, AvailableConsentResSchema(many=True))
@logged_in_required()
def get_available_consents_by_application_uuid(application_uuid: UUID, current_user):
    return ConsentService.get_available_consents_by_application_uuid(
        current_user.id, application_uuid
    )

#permette di aggiungere un consenso ad un app se il dc/dpo è owner/manager di essa
@consent_bp.route("/application/<application_uuid>", methods=["POST"])
@consent_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@consent_bp.arguments(AvailableConsentContentReqSchema, location="json", as_kwargs=True)
@consent_bp.response(201, AvailableConsentResSchema)
@dc_or_dpo_required()
def add_available_consent_to_managed_application(application_uuid: UUID, content: str, current_user):
    return ConsentService.add_available_consent_to_managed_application(
        current_user.id, application_uuid, content
    )

#permette di eliminare un consenso ad un app se il dc/dpo è owner/manager di essa conoscendo il suo uuid
@consent_bp.route("/application/<application_uuid>/<available_consent_uuid>", methods=["DELETE"])
@consent_bp.arguments(ApplicationAndAvailableConsentUuidReqSchema, location="path", as_kwargs=True)
@dc_or_dpo_required()
def remove_available_consent_from_managed_application(application_uuid: UUID, available_consent_uuid: UUID, current_user):
    ConsentService.remove_available_consent_from_managed_application(
        current_user.id, application_uuid, available_consent_uuid
    )
    return "", 204

# permette di ottenere per il DS i consensi di una app nella casa selezionata con stato given / not-given
@consent_bp.route("/home/<smart_home_uuid>/application/<application_uuid>", methods=["GET"])
@consent_bp.arguments(SmartHomeAndApplicationUuidReqSchema, location="path", as_kwargs=True)
@consent_bp.response(200, ConsentStateResSchema(many=True))
@ds_required()
def get_consents_state_by_smart_home_uuid_and_application_uuid(smart_home_uuid: str, application_uuid: UUID, current_user):
    return ConsentService.get_consents_state_by_ds_id_and_smart_home_uuid_and_application_uuid(
        current_user.id, smart_home_uuid, application_uuid
    )

# permette di impostare a given determinati consensi di una app nella casa selezionata
# se consenso già dato non fa nulla
# PUO ESSERE ESPANSA ALLA REVOCA SE DECIDIAMO DI PASSARE DIRETTAMENTE E NON DALLE RIGHT REQUEST
@consent_bp.route("/home/<smart_home_uuid>/application/<application_uuid>", methods=["PUT"])
@consent_bp.arguments(SmartHomeAndApplicationUuidReqSchema, location="path", as_kwargs=True)
@consent_bp.arguments(AvailableConsentsReqSchema, location="json", as_kwargs=True)
@ds_required()
def set_given_consents_by_smart_home_uuid_and_application_uuid(smart_home_uuid: str, application_uuid: UUID, selected_consents: list[UUID], current_user):
    ConsentService.set_given_consents_by_ds_id_and_smart_home_uuid_and_application_uuid(
        current_user.id, smart_home_uuid, application_uuid, selected_consents
    )
    return "", 204
