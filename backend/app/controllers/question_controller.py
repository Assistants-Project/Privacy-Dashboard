from typing import List
from uuid import UUID

from flask_smorest import Blueprint

from ..schemas import (
    ApplicationUuidReqSchema,
    QuestionnaireReqSchema,
    QuestionnaireResSchema,
    QuestionResSchema,
)
from ..services import AnswerReqDict, QuestionService
from ..utils import dc_or_dpo_required

question_bp = Blueprint(
    "Questions API",
    "question_bp",
    url_prefix="/api/questions",
    description="Endpoints for questions",
)


@question_bp.route("/questionnaire", methods=["GET"])
@question_bp.response(200, QuestionResSchema(many=True))
@dc_or_dpo_required()
def get_questionnaire_questions(current_user):
    return QuestionService.get_questionnaire_questions()


@question_bp.route(
    "/submit-questionnaire/application/<application_uuid>", methods=["PUT"]
)
@question_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@question_bp.arguments(QuestionnaireReqSchema, location="json", as_kwargs=True)
@question_bp.response(200, QuestionnaireResSchema)
@dc_or_dpo_required()
def submit_questionnaire_by_managed_application_uuid(
    application_uuid: UUID,
    answers: List[AnswerReqDict],
    check_required: bool,
    current_user,
):
    return QuestionService.submit_questionnaire_by_managed_application_uuid(
        current_user.id, application_uuid, answers, check_required
    )


@question_bp.route(
    "/view-questionnaire/application/<application_uuid>", methods=["GET"]
)
@question_bp.arguments(ApplicationUuidReqSchema, location="path", as_kwargs=True)
@question_bp.response(200, QuestionnaireResSchema)
@dc_or_dpo_required()
def view_questionnaire_by_managed_application_uuid(
    application_uuid: UUID,
    current_user,
):
    return QuestionService.view_questionnaire_by_managed_application_uuid(
        current_user.id, application_uuid
    )
