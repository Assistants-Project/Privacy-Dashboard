from typing import Iterator, List, Tuple, TypedDict
from uuid import UUID

from sqlalchemy import Row

from ..extensions import db
from ..models import Evaluation, Question, QuestionApplication, QuestionType


class QuestionAnsweredDict(TypedDict):
    question_id: int
    answer_content: str
    evaluation: Evaluation | None


class QuestionRepository:
    @staticmethod
    def get_questions_by_type(type: QuestionType) -> Iterator[Question]:
        statement = (
            db.select(Question).where(Question.type == type).order_by(Question.id)
        )
        return db.session.scalars(statement)

    @staticmethod
    def get_question_by_uuid(question_uuid: UUID) -> Row | None:
        statement = db.select(
            Question.id,
            Question.green_choices,
            Question.orange_choices,
            Question.red_choices,
        ).where(Question.uuid == question_uuid)
        return db.session.execute(statement).first()

    @staticmethod
    def submit_questionnaire_by_application_uuid(
        application_id: int,
        questions_answered: List[QuestionAnsweredDict],
    ) -> None:
        for answer in questions_answered:
            question_application = db.session.get(
                QuestionApplication,
                {
                    "question_id": answer["question_id"],
                    "application_id": application_id,
                },
            )
            if question_application is None:
                question_application = QuestionApplication(
                    question_id=answer["question_id"],
                    application_id=application_id,
                    answer_content=answer["answer_content"],
                    evaluation=answer["evaluation"],
                )
                db.session.add(question_application)
            else:
                question_application.answer_content = answer["answer_content"]
                question_application.evaluation = answer["evaluation"]
        db.session.commit()

    @staticmethod
    def get_questionnaire_summary_by_application_id(
        application_id: int,
    ) -> Iterator[Tuple[QuestionApplication, Question]]:
        statement = db.select(QuestionApplication, Question).join(
            QuestionApplication.question.and_(
                QuestionApplication.application_id == application_id,
                Question.type == QuestionType.QUESTIONNAIRE,
            )
        )
        return db.session.execute(statement)
