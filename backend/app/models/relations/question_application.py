from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class QuestionApplication(db.Model):
    __tablename__ = "question_application_relations"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True
    )
    answer_content = mapped_column(Text, nullable=False)

    question: Mapped["Question"] = relationship(  # noqa: F821 # type: ignore
        back_populates="answers"
    )
    application: Mapped["Application"] = relationship(  # noqa: F821 # type: ignore
        back_populates="answers"
    )
