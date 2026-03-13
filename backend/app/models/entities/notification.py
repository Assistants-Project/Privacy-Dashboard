import enum
from datetime import datetime
from typing import List

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
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
    CONSENT_GRANTED = "CONSENT_GRANTED"


class Notification(db.Model):
    """Model for a notification mapped to the table `notifications`.

    A `Notification` instance corresponds to a notification received by one or more users
    after an event of a specific type is performed by one user on a specific object
    (either a request or an application).

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        type: An enum that represents the type of event that triggered the notification.
        sent_at: A datetime object that represents the date and time the notification was sent.
            It is set to the current date and time by default.
        sender_id: A foreign key ID of the sender of the notification.
        sender_email: A snapshot of the sender email kept for audit when the sender user is deleted.
        application_id: A foreign key ID of the application that generated the notification, if any.
        request_id: A foreign key ID of the request that generated the notification, if any.
        processing_context_id: A foreign key ID of the opaque processing context associated to the notification, if any.
        payload: Optional audit payload associated with the notification.
        sender: A user who performed the event that generated the notification.
            Represents a many-to-one relationship with the `User` class.
        application: An application which generated the notification, if any.
            Represents a many-to-one relationship with the `Application` class.
        request: A request which generated the notification, if any.
            Represents a many-to-one relationship with the `Request` class.
        processing_context: The opaque processing context associated with the notification, if any.
            Represents a many-to-one relationship with the `ProcessingContext` class.
        receivers: A list of `UserNotification` instances.
            Represents a one-to-many relationship with the `UserNotification` class.
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    type = mapped_column(Enum(NotificationType, validate_strings=True), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(default=datetime.now())
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    sender_email: Mapped[str | None]
    # nullable many-to-one to each possible object that generates a notification
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.id", ondelete="SET NULL"), default=None
    )
    request_id: Mapped[int | None] = mapped_column(
        ForeignKey("requests.id", ondelete="SET NULL"), default=None
    )
    processing_context_id: Mapped[int | None] = mapped_column(
        ForeignKey("processing_contexts.id", ondelete="SET NULL"),
        default=None,
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, default=None)

    sender: Mapped["User | None"] = relationship(  # noqa: F821 # type: ignore
        back_populates="sent_notifications"
    )
    application: Mapped["Application | None"] = relationship(  # noqa: F821 # type: ignore
        back_populates="generated_notifications"
    )
    request: Mapped["Request | None"] = relationship(  # noqa: F821 # type: ignore
        back_populates="generated_notifications"
    )
    processing_context: Mapped["ProcessingContext | None"] = relationship(  # noqa: F821 # type: ignore
        back_populates="notifications"
    )
    receivers: Mapped[List["UserNotification"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="notification",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Notification(id={self.id!r}, type={self.type!r}, sent_at={self.sent_at!r})"
