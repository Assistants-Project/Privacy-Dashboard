import enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class Evaluation(enum.Enum):
    GREEN = "GREEN"
    ORANGE = "ORANGE"
    RED = "RED"


class Application(db.Model):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    description = mapped_column(Text, nullable=True)
    evaluation = mapped_column(Enum(Evaluation, validate_strings=True), nullable=True)
    questionnaire_summary = mapped_column(Text, nullable=True)
    privacy_notice_id: Mapped[int | None] = mapped_column(
        ForeignKey("privacy_notices.id", ondelete="SET NULL")
    )

    privacy_notice: Mapped["PrivacyNotice"] = relationship(  # noqa: F821 # type: ignore
        back_populates="applications"
    )
    questions: Mapped[List["QuestionApplicationRelation"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="application", cascade="all, delete-orphan", passive_deletes=True
    )
