from flask_jwt_extended import current_user
from flask_smorest import Blueprint

from ..schemas import ApplicationResSchema
from ..services import ApplicationService
from ..utils import dc_or_dpo_required

application_bp = Blueprint(
    "Applications API",
    "application_bp",
    url_prefix="/api/applications",
    description="Endpoints for applications",
)


@application_bp.route("/my-managed", methods=["GET"])
@application_bp.response(200, ApplicationResSchema(many=True))
@dc_or_dpo_required()
def get_applications_by_current_dc_or_dpo():
    return ApplicationService.get_applications_by_dc_or_dpo_id(current_user.id)
