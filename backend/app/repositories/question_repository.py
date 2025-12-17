from typing import Iterator

from ..extensions import db
from ..models import Question, QuestionType


class QuestionRepository:
    @staticmethod
    def get_questions_by_type(type: QuestionType) -> Iterator[Question]:
        statement = (
            db.select(Question).where(Question.type == type).order_by(Question.id)
        )
        return db.session.scalars(statement)
