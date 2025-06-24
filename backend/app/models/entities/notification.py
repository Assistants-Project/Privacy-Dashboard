import enum
from datetime import datetime
from typing import List

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class NotificationType(enum.Enum):
    PRIVACY_NOTICE_ASSOCIATED = "PRIVACY_NOTICE_ASSOCIATED"
    PRIVACY_NOTICE_EDITED = "PRIVACY_NOTICE_EDITED"
    QUESTIONNAIRE_CARRIED_OUT = "QUESTIONNAIRE_CARRIED_OUT"
    QUESTIONNAIRE_EDITED = "QUESTIONNAIRE_EDITED"
    PRIVACY_IMPACT_ASSESSMENT_CARRIED_OUT = "PRIVACY_IMPACT_ASSESSMENT_CARRIED_OUT"
    PRIVACY_IMPACT_ASSESSMENT_EDITED = "PRIVACY_IMPACT_ASSESSMENT_EDITED"
    REQUEST_SUBMITTED = "REQUEST_SUBMITTED"
    REQUEST_ANSWERED = "REQUEST_ANSWERED"
    REQUEST_STATUS_UPDATED = "REQUEST_STATUS_UPDATED"


class Notification(db.Model):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    type = mapped_column(Enum(NotificationType, validate_strings=True), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(default=datetime.now())
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # nullable many-to-one to each possible object that generates a notification
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), default=None
    )
    request_id: Mapped[int | None] = mapped_column(
        ForeignKey("requests.id", ondelete="CASCADE"), default=None
    )

    sender: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        back_populates="sent_notifications"
    )
    application: Mapped["Application | None"] = relationship(  # noqa: F821 # type: ignore
        back_populates="generated_notifications"
    )
    request: Mapped["Request | None"] = relationship(  # noqa: F821 # type: ignore
        back_populates="generated_notifications"
    )
    receivers: Mapped[List["UserNotification"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="notification",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
