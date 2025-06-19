import uuid
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UUID

from ..extensions import db


class SmartHome(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(UUID(), default=uuid.uuid4, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]

    users: Mapped[List["UserSmartHomeRelation"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
