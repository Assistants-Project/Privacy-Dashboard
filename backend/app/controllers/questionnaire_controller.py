from typing import List
from uuid import UUID

from flask_smorest import Blueprint

from ..schemas import ApplicationUuidReqSchema, QuestionnaireReqSchema, QuestionnaireResSchema, QuestionResSchema
from ..services import AnswerReqDict, QuestionService
from ..utils import dc_or_dpo_required

questionnaire_bp = Blueprint(
    "Questionnaires API",
    "questionnaire_bp",
    url_prefix="/api/questionnaires",
    description="Endpoints for questionnaires",
)


@questionnaire_bp.route("/template", methods=["GET"])
@questionnaire_bp.response(200, QuestionResSchema(many=True))
@dc_or_dpo_required()
def get_questionnaire_template(current_user):
    return QuestionService.get_questionnaire_questions()


@questionnaire_bp.route("/managed-application/<application_uuid>", methods=["GET"])
@questionnaire_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@questionnaire_bp.response(200, QuestionnaireResSchema)
@dc_or_dpo_required()
def get_questionnaire_by_managed_application_uuid(application_uuid: UUID, current_user):
    return QuestionService.view_questionnaire_by_managed_application_uuid(current_user.id, application_uuid)


@questionnaire_bp.route("/managed-application/<application_uuid>", methods=["PUT"])
@questionnaire_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@questionnaire_bp.arguments(QuestionnaireReqSchema, location="json", as_kwargs=True)
@questionnaire_bp.response(200, QuestionnaireResSchema)
@dc_or_dpo_required()
def submit_questionnaire_by_managed_application_uuid(application_uuid: UUID, answers: List[AnswerReqDict], check_required: bool, current_user):
    return QuestionService.submit_questionnaire_by_managed_application_uuid(current_user.id, application_uuid, answers, check_required)
