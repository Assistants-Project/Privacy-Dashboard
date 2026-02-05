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
    PrivacyImpactAssessmentReqSchema,
    PrivacyImpactAssessmentResSchema,
    
)
from ..services import ApplicationService
from ..utils import dc_or_dpo_required, dc_required, ds_required, logged_in_required
from ..models import UserRole

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
    return ApplicationService.get_available_applications_service(current_user)

#serve per permettere ad un data controller di assegnarsi ad un app (visto che manca un marketplace che lo aggiunge)
@application_bp.route("/managed/<application_uuid>", methods=["POST"])
@application_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_required()
def claim_managed_application(application_uuid, current_user):
    created = ApplicationService.claim_application(current_user, application_uuid)
    return "", 201 if created else 204

#serve per permettere ad un data controller di assegnare un dpo a scelta ad un app se conosce il suo uuid
@application_bp.route("/managed/<application_uuid>/dpo", methods=["PUT"])
@application_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_required()
def assign_dpo_to_application(application_uuid, current_user):
    payload = request.get_json(silent=True) or {}
    dpo_uuid = payload.get("dpo_uuid")
    created = ApplicationService.assign_dpo_to_managed_application(
        current_user, application_uuid, dpo_uuid
    )
    return "", 201 if created else 204

@application_bp.route("/refresh", methods=["POST"])
@application_bp.response(202, description="Refresh started")
@logged_in_required()
def refresh_apps(current_user):
    ApplicationService.update_apps_database_from_all_sources(current_user)
    if current_user.role == UserRole.DATA_SUBJECT:
        return "Apps updated from Smartotum Installed App of " + current_user.email, 202
    else:
        return "Apps updated from Marketplace " + current_user.email, 202
    


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
@application_bp.response(200, PrivacyImpactAssessmentResSchema)
@dc_or_dpo_required()
def get_pia_by_managed_application_uuid(application_uuid: str, current_user):
    pia_content = ApplicationService.get_pia_by_managed_application_uuid(
        current_user.id, application_uuid
    )
    return {"application_uuid": application_uuid, "content": pia_content}


@application_bp.route("/managed-application/<application_uuid>/pia", methods=["PUT"])
@application_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@application_bp.arguments(PrivacyImpactAssessmentReqSchema, location="json", as_kwargs=True)
@dc_or_dpo_required()
def submit_pia_by_managed_application_uuid(application_uuid: str, content: dict, current_user):
    ApplicationService.submit_pia_by_managed_application_uuid(
        current_user.id, application_uuid, content
    )
    return "", 204
