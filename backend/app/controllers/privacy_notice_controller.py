from uuid import UUID

from flask_smorest import Blueprint

from ..schemas import ApplicationUuidReqSchema, PrivacyNoticeResSchema
from ..services import PrivacyNoticeService
from ..utils import dc_or_dpo_required, get_current_user_from_claims

privacy_notice_bp = Blueprint(
    "Privacy Notices API",
    "privacy_notice_bp",
    url_prefix="/api/privacy-notices",
    description="Endpoints for privacy notices",
)


@privacy_notice_bp.route("/managed-application/<application_uuid>", methods=["GET"])
@privacy_notice_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@privacy_notice_bp.response(200, PrivacyNoticeResSchema)
@dc_or_dpo_required()
def get_privacy_notice_by_managed_application_uuid(application_uuid: UUID):
    user = get_current_user_from_claims()
    return PrivacyNoticeService.get_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
        user.id, application_uuid
    )
