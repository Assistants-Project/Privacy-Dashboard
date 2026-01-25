from flask import Response, request
from flask_smorest import Blueprint

from .. import initial_data
from ..exceptions import MissingTemplateException
from ..schemas import (
    ApplicationResSchema,
    ApplicationUuidReqSchema,
    SmartHomeUuidReqSchema,
    ApplicationCatalogItemResSchema,
    InstalledApplicationWithManagersResSchema,
    
)
from ..services import ApplicationService
from ..utils import dc_or_dpo_required, ds_required, logged_in_required

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

#find better name
#for data controller to see all the apps
@application_bp.route("/catalog", methods=["GET"])
@application_bp.response(200, ApplicationCatalogItemResSchema(many=True))
@dc_or_dpo_required()
def get_available_applications(current_user):
    return ApplicationService.get_available_applications_service()


@application_bp.route("/home/<smart_home_uuid>", methods=["GET"])
@application_bp.arguments(SmartHomeUuidReqSchema, location="path", as_kwargs=True)
@application_bp.response(200, InstalledApplicationWithManagersResSchema(many=True))
@ds_required()
def get_installed_applications(smart_home_uuid: str, current_user):
    return ApplicationService.get_applications_by_ds_id_and_smart_home_uuid(
        current_user.id, smart_home_uuid
    )


@application_bp.route("/pia-template", methods=["GET"])
@dc_or_dpo_required()
def get_pia_template(current_user):
    if initial_data.pia_template is None:
        raise MissingTemplateException(
            "Template of Privacy Impact Assessment not found!"
        )
    return Response(initial_data.pia_template, mimetype="application/json", status=200)


@application_bp.route("/managed-application/<application_uuid>/pia", methods=["GET"])
@application_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_or_dpo_required()
def get_pia_by_managed_application_uuid(application_uuid: str, current_user):
    return Response(
        ApplicationService.get_pia_by_managed_application_uuid(
            current_user.id, application_uuid
        ),
        mimetype="application/json",
        status=200,
    )


@application_bp.route("/managed-application/<application_uuid>/pia", methods=["PUT"])
@application_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_or_dpo_required()
def submit_pia_by_managed_application_uuid(application_uuid: str, current_user):
    ApplicationService.submit_pia_by_managed_application_uuid(
        current_user.id, application_uuid, request.get_json(silent=True)
    )
    return "", 204
