from flask_smorest import Blueprint

from ..schemas import QuestionResSchema
from ..services import QuestionService
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
def get_questionnaire(current_user):
    return QuestionService.get_questionnaire()
