from typing import List
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class SmartHome(db.Model):
    __tablename__ = "smart_homes"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]

    owned_by_users: Mapped[List["UserSmartHome"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    installed_applications: Mapped[List["UserSmartHomeApplication"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    given_consents: Mapped[List["UserSmartHomeAvailableConsent"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
