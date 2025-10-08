from uuid import UUID

from flask_smorest import Blueprint

from ..models import UserRole
from ..schemas import ApplicationUuidReqSchema, UserResSchema, UserRoleReqSchema
from ..services import UserService
from ..utils import dc_or_dpo_required, get_current_user_from_claims

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
    user = get_current_user_from_claims()
    return UserService.get_users_by_dc_or_dpo_id_and_application_uuid_and_user_role(
        user.id, application_uuid, role
    )


@user_bp.route("/contacts", methods=["GET"])
@user_bp.response(200, UserResSchema(many=True))
@dc_or_dpo_required()
def get_dc_or_dpo_contacts():
    user = get_current_user_from_claims()
    return UserService.get_contacts_by_dc_or_dpo_id(user.id)
