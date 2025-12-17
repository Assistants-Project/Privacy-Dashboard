from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db
from ..entities.application import Evaluation


class QuestionApplication(db.Model):
    """Association object representing the bi-directional many-to-many
    relationship between `Question` and `Application`, mapped to
    the table `question_application_relations`.

    A `QuestionApplication` instance represents a unique combination of a
    `Question` instance and a `Application` instance, and means that such
    question was answered by such application, storing the specific answer.

    Attributes:
        question_id: A foreign key ID of the question that was answered.
        application_id: A foreign key ID of the application that answered the question.
        answer_content: A text field that represents the content of the answer.
        evaluation: An Enum evaluation of the given answer that represents the
            level of compliancy to the GDPR regulations.
        question: A question that was answered.
            Represents a many-to-one relationship with the `Question` class.
        application: An application that answered the question.
            Represents a many-to-one relationship with the `Application` class.
    """

    __tablename__ = "question_application_relations"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True
    )
    answer_content = mapped_column(Text, nullable=False)
    evaluation = mapped_column(Enum(Evaluation, validate_strings=True), nullable=True)

    question: Mapped["Question"] = relationship(  # noqa: F821 # type: ignore
        back_populates="answers"
    )
    application: Mapped["Application"] = relationship(  # noqa: F821 # type: ignore
        back_populates="answers"
    )

    def __repr__(self) -> str:
        return f"QuestionApplication(question_id={self.question_id}, \
            application_id={self.application_id}, answer_content={self.answer_content})"
