from flask_smorest import Blueprint

from ..schemas import ApplicationResSchema, SmartHomeUuidReqSchema
from ..services import ApplicationService
from ..utils import dc_or_dpo_required, ds_required

application_bp = Blueprint(
    "Applications API",
    "application_bp",
    url_prefix="/api/applications",
    description="Endpoints for applications",
)


@application_bp.route("/managed", methods=["GET"])
@application_bp.response(200, ApplicationResSchema(many=True))
@dc_or_dpo_required()
def get_managed_applications(current_user):
    return ApplicationService.get_applications_by_dc_or_dpo_id(current_user.id)


@application_bp.route("/home/<smart_home_uuid>", methods=["GET"])
@application_bp.arguments(SmartHomeUuidReqSchema, location="path", as_kwargs=True)
@application_bp.response(200, ApplicationResSchema(many=True))
@ds_required()
def get_installed_applications(smart_home_uuid: str, current_user):
    return ApplicationService.get_applications_by_ds_id_and_smart_home_uuid(
        current_user.id, smart_home_uuid
    )
