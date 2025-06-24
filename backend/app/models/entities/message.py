from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    content = mapped_column(Text, nullable=False)
    attachment: Mapped[str | None]
    sent_at: Mapped[datetime] = mapped_column(default=datetime.now())
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_read: Mapped[bool] = mapped_column(default=False)

    sender: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        foreign_keys=[sender_id], back_populates="sent_messages"
    )
    receiver: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        foreign_keys=[receiver_id], back_populates="received_messages"
    )
