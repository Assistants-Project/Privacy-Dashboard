from flask import Response, request
from flask_smorest import Blueprint

from .. import initial_data
from ..schemas import (
    ApplicationResSchema,
    ApplicationUuidReqSchema,
    SmartHomeUuidReqSchema,
)
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


@application_bp.route("/pia-template", methods=["GET"])
@dc_or_dpo_required()
def get_pia_template(current_user):
    if initial_data.pia_template is None:
        return {"message": "Template of Privacy Impact Assessment not found!"}, 404
    return Response(initial_data.pia_template, mimetype="application/json", status=200)


@application_bp.route("/application/<application_uuid>/pia-template", methods=["POST"])
@application_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_or_dpo_required()
def submit_pia_by_managed_application_uuid(application_uuid: str, current_user):
    payload = request.get_json()
    if payload is None:
        return {
            "message": "JSON body with required Privacy Impact Assessment data is missing!"
        }, 400
    ApplicationService.submit_pia_by_managed_application_uuid(
        current_user.id, application_uuid, payload
    )
    return {"message": "Privacy Impact Assessment submitted successfully."}, 204
