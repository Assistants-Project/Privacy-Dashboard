from uuid import UUID
from flask_smorest import Blueprint
from ..schemas import ApplicationAndUserEmailReqSchema, ApplicationCreateReqSchema, ApplicationUuidReqSchema, InstalledApplicationResSchema, ManagedApplicationResSchema, OptionalApplicationUuidReqSchema, SmartHomeUuidReqSchema
from ..services import ApplicationService, SmartotumService
from ..utils import dc_or_dpo_required, dc_required, ds_required

application_bp = Blueprint(
    "Applications API",
    "application_bp",
    url_prefix="/api/applications",
    description="Endpoints for applications",
)

@application_bp.route("/home/<smart_home_uuid>", methods=["GET"])
@application_bp.arguments(SmartHomeUuidReqSchema, location="path", as_kwargs=True)
@application_bp.arguments(OptionalApplicationUuidReqSchema, location="query", as_kwargs=True)
@application_bp.response(200, InstalledApplicationResSchema(many=True))
@ds_required()
def get_installed_applications(smart_home_uuid: str, current_user, application_uuid: UUID | None = None):
    return ApplicationService.get_applications_by_ds_id_and_smart_home_uuid(
        current_user.id, smart_home_uuid, application_uuid
    )

#Flusso creazione applicazione manualmente da parte di un Data Controller
@application_bp.route("", methods=["POST"])
@application_bp.arguments(ApplicationCreateReqSchema, location="json", as_kwargs=True)
@application_bp.response(201, ManagedApplicationResSchema)
@dc_required()
def create_application(name: str,current_user,description: str | None = None,available_consents: list[str] | None = None):
    created_application = ApplicationService.create_application_managed_by_data_controller(current_user, name, description, available_consents)
    return created_application

#Recupera app gestite da un data controller / dpo
@application_bp.route("/managed", methods=["GET"])
@application_bp.arguments(OptionalApplicationUuidReqSchema, location="query", as_kwargs=True)
@application_bp.response(200, ManagedApplicationResSchema(many=True))
@dc_or_dpo_required()
def get_managed_applications(current_user, application_uuid: UUID | None = None):
    return ApplicationService.get_applications_by_dc_or_dpo_id(current_user, application_uuid)

#Flusso -> Data Controller assegna un app ad un DPO
@application_bp.route("/managed/<application_uuid>/dpo/<user_email>", methods=["PUT"])
@application_bp.arguments(ApplicationAndUserEmailReqSchema, location="path", as_kwargs=True)
@dc_required()
def assign_dpo_to_application(application_uuid, user_email, current_user):
    result = ApplicationService.assign_dpo_to_managed_application(
        current_user, application_uuid, user_email
    )
    if result == "created":
        return "", 201
    if result == "replaced":
        return "", 200
    return "", 204

@application_bp.route("/managed/<application_uuid>/dpo", methods=["DELETE"])
@application_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_required()
def remove_dpo_from_application(application_uuid, current_user):
    ApplicationService.remove_dpo_from_managed_application(current_user, application_uuid)
    return "", 204

#Flusso -> Data Controller Owner dell'app assegna un altro Data Controller come manager
@application_bp.route("/managed/<application_uuid>/managers/<user_email>", methods=["PUT"])
@application_bp.arguments(ApplicationAndUserEmailReqSchema, location="path", as_kwargs=True)
@dc_required()
def add_data_controller_manager_to_application(application_uuid, user_email, current_user):
    created = ApplicationService.add_data_controller_manager_to_owned_application(current_user, application_uuid, user_email)
    return "", 201 if created else 204

#Flusso -> Data Controller Owner rimiove un determinato Data Controller da manager
@application_bp.route("/managed/<application_uuid>/managers/<user_email>", methods=["DELETE"])
@application_bp.arguments(ApplicationAndUserEmailReqSchema, location="path", as_kwargs=True)
@dc_required()
def remove_data_controller_manager_from_application(application_uuid, user_email, current_user):
    ApplicationService.remove_data_controller_manager_from_owned_application(current_user, application_uuid, user_email)
    return "", 204

#Flusso di refresh applicazioni da smartotum
@application_bp.route("/refresh", methods=["POST"])
@application_bp.response(202, description="Refresh started")
@ds_required()
def refresh_apps(current_user):
    SmartotumService.update_installed_application_for_user(current_user)
    return "Apps updated from Smartotum Installed App of " + current_user.email, 202
