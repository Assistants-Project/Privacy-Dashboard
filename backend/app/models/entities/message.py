from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class Message(db.Model):
    """Model for a message mapped to the table `messages`.

    A `Message` instance corresponds to a message sent between two users at
    a specific date and time. A message can be read or unread and optionally
    have an attachment.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        uuid: A unique randomly generated UUID that identifies the message.
        content: A string that represents the content of the message.
        attachment: An optional string that represents the path to the attachment of the message, if any.
        sent_at: A datetime object that represents the date and time the message was sent.
            It is set to the current date and time by default.
        sender_id: A foreign key ID of the sender of the message.
        receiver_id: A foreign key ID of the receiver of the message.
        is_read: A `boolean` that represents whether the message was read or not by the receiver.
            It is set to `False` by default.
        sender: A user who sent the message.
            Represents a many-to-one relationship with the `User` class.
        receiver: A user who received the message.
            Represents a many-to-one relationship with the `User` class.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, uuid={self.uuid!r}, content={self.content!r}, attachment={self.attachment!r}, sent_at={self.sent_at!r}, is_read={self.is_read!r})"
