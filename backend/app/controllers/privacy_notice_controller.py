from uuid import UUID

from flask import Response
from flask_smorest import Blueprint

from .. import initial_data
from ..exceptions import MissingTemplateException
from ..schemas import (
    ApplicationAndPrivacyNoticeUuidReqSchema,
    ApplicationUuidReqSchema,
    PrivacyNoticeReqSchema,
    PrivacyNoticeResSchema,
)
from ..services import PrivacyNoticeService
from ..utils import dc_or_dpo_required, ds_required

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
def get_privacy_notice_by_managed_application_uuid(
    application_uuid: UUID, current_user
):
    return PrivacyNoticeService.get_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
        current_user.id, application_uuid
    )

@privacy_notice_bp.route("/installed-application/<application_uuid>", methods=["GET"])
@privacy_notice_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@privacy_notice_bp.response(200, PrivacyNoticeResSchema)
@ds_required()
def get_privacy_notice_by_installed_application_uuid(
    application_uuid: UUID, current_user
):
    privacy_notice = PrivacyNoticeService.get_privacy_notice_by_ds_id_and_application_uuid(
        current_user.id, application_uuid
    )
    if privacy_notice is None:
        return Response(status=204)
    return privacy_notice


@privacy_notice_bp.route("/template", methods=["GET"])
@dc_or_dpo_required()
def get_privacy_notice_template(current_user):
    if initial_data.privacy_notice_template is None:
        raise MissingTemplateException("Template of Privacy Notice not found!")
    return Response(
        initial_data.privacy_notice_template, mimetype="application/json", status=200
    )


@privacy_notice_bp.route("/managed-application/<application_uuid>", methods=["POST"])
@privacy_notice_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@privacy_notice_bp.arguments(PrivacyNoticeReqSchema, location="json", as_kwargs=True)
@privacy_notice_bp.response(201, PrivacyNoticeResSchema)
@dc_or_dpo_required()
def write_privacy_notice_by_managed_application_uuid(
    application_uuid: UUID, content: str, current_user
):
    return (
        PrivacyNoticeService.write_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
            current_user.id, application_uuid, content
        )
    )


@privacy_notice_bp.route(
    "/managed-application/<application_uuid>/privacy-notice/<privacy_notice_uuid>",
    methods=["PUT"],
)
@privacy_notice_bp.arguments(
    ApplicationAndPrivacyNoticeUuidReqSchema, location="path", as_kwargs=True
)
@privacy_notice_bp.response(201, PrivacyNoticeResSchema)
@dc_or_dpo_required()
def associate_privacy_notice_by_managed_application_uuid(
    application_uuid: UUID, privacy_notice_uuid: UUID, current_user
):
    return PrivacyNoticeService.associate_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
        current_user.id, application_uuid, privacy_notice_uuid
    )


@privacy_notice_bp.route("/managed-application/<application_uuid>", methods=["PUT"])
@privacy_notice_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@privacy_notice_bp.arguments(PrivacyNoticeReqSchema, location="json", as_kwargs=True)
@privacy_notice_bp.response(200, PrivacyNoticeResSchema)
@dc_or_dpo_required()
def edit_privacy_notice_by_managed_application_uuid(
    application_uuid: UUID, content: str, current_user
):
    return (
        PrivacyNoticeService.edit_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
            current_user.id, application_uuid, content
        )
    )


@privacy_notice_bp.route("/managed-application/<application_uuid>", methods=["DELETE"])
@privacy_notice_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_or_dpo_required()
def remove_privacy_notice_by_managed_application_uuid(
    application_uuid: UUID, current_user
):
    PrivacyNoticeService.remove_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
        current_user.id, application_uuid
    )
    return "", 204
