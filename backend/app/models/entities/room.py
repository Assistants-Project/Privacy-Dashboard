from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class Room(db.Model):
    """Model for a room mapped to the table `rooms`.

    Attributes:
        room_id: Auto-incremented primary key.
        room_uuid: Unique identifier for the room.
        home_id: Foreign key referencing the smart home this room belongs to.
        name: Human readable name of the room (e.g., Living Room).
        category: Optional category (e.g., Bedroom, Kitchen).
    """

    __tablename__ = "rooms"

    room_id: Mapped[int] = mapped_column(primary_key=True)
    room_uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    home_id: Mapped[int] = mapped_column(
        ForeignKey("smart_homes.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str]
    category: Mapped[Optional[str]]

    smart_home: Mapped["SmartHome"] = relationship(back_populates="rooms")  # type: ignore

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return (
            f"Room(room_id={self.room_id}, room_uuid={self.room_uuid}, "
            f"home_id={self.home_id}, name={self.name!r}, category={self.category!r})"
        )
