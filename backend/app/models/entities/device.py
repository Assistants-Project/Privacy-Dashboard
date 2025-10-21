from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...extensions import db


class Device(db.Model):
    """Model for a device mapped to the table `devices`.

    Attributes:
        device_id: Auto-incremented primary key.
        device_uuid: Unique identifier for the device, is the Smartotum internal one
        home_id: Foreign key referencing the smart home this device belongs to.
        room_id: Foreign key referencing the room where the decive is installed in the smart home.
        name: Human readable name of the room (e.g., Living Room).
        topic_name: Topic name from Smartotum
    """

    __tablename__ = "devices"

    device_id: Mapped[int] = mapped_column(primary_key=True)
    device_uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    home_id: Mapped[int] = mapped_column(
        ForeignKey("smart_homes.id", ondelete="CASCADE"), nullable=False
    )
    room_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str]
    topic_name: Mapped[Optional[str]] = mapped_column(nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return (
            f"Device(device_id={self.device_id}, device_uuid={self.device_uuid}, "
            f"home_id={self.home_id}, room_id={self.room_id}, name={self.name!r}, "
            f"topic_name={self.topic_name!r})"
        )
