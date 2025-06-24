from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserNotification(db.Model):
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
