from ...extensions import ma


class AnswerSchema(ma.Schema):
    question_uuid = ma.UUID(required=True, allow_none=False)
    answer_content = ma.String(required=True, allow_none=False)


class QuestionnaireReqSchema(ma.Schema):
    answers = ma.Nested(AnswerSchema, many=True, required=True, allow_none=False)
    check_required = ma.Boolean(required=True, allow_none=False)
