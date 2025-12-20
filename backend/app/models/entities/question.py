import enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class QuestionType(enum.Enum):
    QUESTIONNAIRE = "QUESTIONNAIRE"
    PRIVACY_IMPACT_ASSESSMENT = "PRIVACY_IMPACT_ASSESSMENT"


class Question(db.Model):
    """Model for a question mapped to the table `questions`.

    A `Question` instance corresponds to one question of either a questionnaire
    or a privacy impact assessment. It can either be an open question or a
    multiple choice question.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        uuid: A unique randomly generated UUID that identifies the question.
        content: A text field that represents the content of the question.
        additional_information: An optional text field that represents any additional information
            that may be relevant to the question.
        choices: An optional text field that represents the choices of a multiple choice question,
            assuming that the choices are stored as a single delimiter-separated string.
        type: An enum that represents whether the question belongs to a questionnaire or
            a privacy impact assessment.
        answers: A list of `QuestionApplication` instances.
            Represents a one-to-many relationship with the `QuestionApplication` class.
    """

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    content = mapped_column(Text, nullable=False)
    additional_information = mapped_column(Text, nullable=True)
    # In case of multiple choice questions, the choices are stored here as a delimiter-separated string
    choices = mapped_column(Text, nullable=True)
    type = mapped_column(Enum(QuestionType, validate_strings=True), nullable=False)

    answers: Mapped[List["QuestionApplication"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="question", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"Question(id={self.id}, content={self.content}, \
            choices={self.choices}, type={self.type})"
