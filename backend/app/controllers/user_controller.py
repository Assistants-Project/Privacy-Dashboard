from uuid import UUID

from flask_jwt_extended import current_user
from flask_smorest import Blueprint

from ..models import UserRole
from ..schemas import ApplicationUuidReqSchema, UserResSchema, UserRoleReqSchema
from ..services import UserService
from ..utils import dc_or_dpo_required

user_bp = Blueprint(
    "Users API",
    "user_bp",
    url_prefix="/api/users",
    description="Endpoints for users",
)


@user_bp.route("/managed-application/<application_uuid>", methods=["GET"])
@user_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@user_bp.arguments(UserRoleReqSchema, location="query", as_kwargs=True)
@user_bp.response(200, UserResSchema(many=True))
@dc_or_dpo_required()
def get_users_by_managed_application_uuid_and_user_role(
    application_uuid: UUID, role: UserRole
):
    return UserService.get_users_by_dc_or_dpo_id_and_application_uuid_and_user_role(
        current_user.id, application_uuid, role
    )
