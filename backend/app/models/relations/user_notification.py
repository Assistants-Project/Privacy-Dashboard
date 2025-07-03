from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserNotification(db.Model):
    """Association object representing the bi-directional many-to-many
    relationship between `User` and `Notification`, mapped to the table
    `user_notification_relations`.

    A `UserNotification` instance represents a unique combination of a
    `User` instance and a `Notification` instance, and indicates whether
    the user has read the notification he received.

    Attributes:
        user_id: A foreign key ID of the user who received the notification.
        notification_id: A foreign key ID of the notification received by the user.
        is_read: A `boolean` that indicates whether the user has read the notification.
            It is set to `False` by default.
        user: A user who received the notification.
            Represents a many-to-one relationship with the `User` class.
        notification: A notification received by the user.
            Represents a many-to-one relationship with the `Notification` class.
    """

    __tablename__ = "user_notification_relations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    notification_id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True
    )
    is_read: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        back_populates="received_notifications"
    )
    notification: Mapped["Notification"] = relationship(  # noqa: F821 # type: ignore
        back_populates="receivers"
    )

    def __repr__(self) -> str:
        return f"UserNotification(user_id={self.user_id!r}, \
            notification_id={self.notification_id!r}, is_read={self.is_read!r})"
