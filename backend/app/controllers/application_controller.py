from flask_smorest import Blueprint

from ..schemas import ApplicationResSchema
from ..services import ApplicationService
from ..utils import dc_or_dpo_required, get_current_user_from_claims

application_bp = Blueprint(
    "Applications API",
    "application_bp",
    url_prefix="/api/applications",
    description="Endpoints for applications",
)


@application_bp.route("/managed", methods=["GET"])
@application_bp.response(200, ApplicationResSchema(many=True))
@dc_or_dpo_required()
def get_managed_applications():
    user = get_current_user_from_claims()
    return ApplicationService.get_applications_by_dc_or_dpo_id(user.id)
