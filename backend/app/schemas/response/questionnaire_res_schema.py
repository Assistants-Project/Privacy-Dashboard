from ...extensions import ma
from ...models import Evaluation, Question, QuestionApplication


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id", "green_choices", "orange_choices", "red_choices", "type")


class QuestionApplicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = QuestionApplication
        include_fk = False
        include_relationships = False
        load_instance = False


class GivenAnswerSchema(ma.Schema):
    question = ma.Nested(QuestionSchema)
    answer = ma.Nested(QuestionApplicationSchema)


class QuestionnaireResSchema(ma.Schema):
    application_evaluation = ma.Enum(
        Evaluation, by_value=True, required=False, allow_none=False, load_default=None
    )
    given_answers = ma.Nested(GivenAnswerSchema, many=True)
