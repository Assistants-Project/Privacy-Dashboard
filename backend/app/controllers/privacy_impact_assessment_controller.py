from flask import Response
from flask_smorest import Blueprint

from ..schemas import ApplicationUuidReqSchema, PrivacyImpactAssessmentReqSchema, PrivacyImpactAssessmentResSchema
from ..services import PrivacyImpactAssessmentService
from ..utils import dc_or_dpo_required

privacy_impact_assessment_bp = Blueprint(
    "Privacy Impact Assessments API",
    "privacy_impact_assessment_bp",
    url_prefix="/api/privacy-impact-assessments",
    description="Endpoints for privacy impact assessments",
)


@privacy_impact_assessment_bp.route("/template", methods=["GET"])
@dc_or_dpo_required()
def get_pia_template(current_user):
    return Response(PrivacyImpactAssessmentService.get_pia_template(), mimetype="application/json", status=200)


@privacy_impact_assessment_bp.route("/managed/<application_uuid>", methods=["GET"])
@privacy_impact_assessment_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@privacy_impact_assessment_bp.response(200, PrivacyImpactAssessmentResSchema)
@dc_or_dpo_required()
def get_pia_by_managed_application_uuid(application_uuid: str, current_user):
    pia_content = PrivacyImpactAssessmentService.get_pia_by_managed_application_uuid(current_user.id, application_uuid)
    return {"application_uuid": application_uuid, "content": pia_content}


@privacy_impact_assessment_bp.route("/managed/<application_uuid>", methods=["PUT"])
@privacy_impact_assessment_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@privacy_impact_assessment_bp.arguments(PrivacyImpactAssessmentReqSchema, location="json", as_kwargs=True)
@dc_or_dpo_required()
def submit_pia_by_managed_application_uuid(application_uuid: str, content: dict, current_user):
    PrivacyImpactAssessmentService.submit_pia_by_managed_application_uuid(current_user.id, application_uuid, content)
    return "", 204


@privacy_impact_assessment_bp.route("/managed/<application_uuid>", methods=["DELETE"])
@privacy_impact_assessment_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@dc_or_dpo_required()
def remove_pia_by_managed_application_uuid(application_uuid: str, current_user):
    PrivacyImpactAssessmentService.remove_pia_by_managed_application_uuid(current_user.id, application_uuid)
    return "", 204
