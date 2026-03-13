from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class ProcessingContext(db.Model):
    """Opaque audit context for a specific Data Subject, application and smart home.

    The row is stable over time and survives even if the DS-home-app relation is later pruned.
    It is the anchor used by rights requests and consent-granted notifications.
    """

    __tablename__ = "processing_contexts"
    __table_args__ = (
        UniqueConstraint(
            "data_subject_user_id",
            "application_id",
            "smart_home_uuid",
            name="uq_processing_context_user_app_home",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    data_subject_user_id: Mapped[int] = mapped_column(nullable=False)
    data_subject_email: Mapped[str] = mapped_column(nullable=False)
    application_id: Mapped[int] = mapped_column(nullable=False)
    application_uuid: Mapped[UUID] = mapped_column(nullable=False)
    application_name: Mapped[str] = mapped_column(nullable=False)
    smart_home_uuid: Mapped[str] = mapped_column(nullable=False)
    user_smart_home_application_relation_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_smart_home_application_relations.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    user_smart_home_application_relation: Mapped["UserSmartHomeApplication | None"] = relationship()  # noqa: F821 # type: ignore
    requests: Mapped[List["Request"]] = relationship(back_populates="processing_context")  # noqa: F821 # type: ignore
    notifications: Mapped[List["Notification"]] = relationship(back_populates="processing_context")  # noqa: F821 # type: ignore

    def __repr__(self) -> str:
        return f"ProcessingContext(id={self.id!r}, uuid={self.uuid!r}, data_subject_user_id={self.data_subject_user_id!r}, application_id={self.application_id!r}, smart_home_uuid={self.smart_home_uuid!r})"
