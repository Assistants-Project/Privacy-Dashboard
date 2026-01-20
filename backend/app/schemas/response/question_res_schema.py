from ...extensions import ma
from ...models import Question


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id", "green_choices", "orange_choices", "red_choices")


class QuestionResSchema(ma.Schema):
    question = ma.Nested(QuestionSchema)
    choices = ma.List(ma.String(), allow_none=True, required=False)
