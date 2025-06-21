import enum
from typing import List

from sqlalchemy import Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class QuestionType(enum.Enum):
    QUESTIONNAIRE = "QUESTIONNAIRE"
    PRIVACY_IMPACT_ASSESSMENT = "PRIVACY_IMPACT_ASSESSMENT"


class Question(db.Model):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    content = mapped_column(Text, nullable=False)
    # In case of multiple choice questions, the choices are stored here as a delimiter-separated string
    choices = mapped_column(Text, nullable=True)
    type = mapped_column(Enum(QuestionType, validate_strings=True), nullable=False)

    answers: Mapped[List["QuestionApplication"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="question", cascade="all, delete-orphan", passive_deletes=True
    )
