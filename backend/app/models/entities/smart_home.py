from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db

if TYPE_CHECKING:
    from .sifis.db import DbRule, DbEntity


class SmartHome(db.Model):
    """Model for a smart home mapped to the table `smart_homes`.

    A `SmartHome` instance corresponds to a smart home owned by one or more Data Subjects,
    in which one or more applications can be installed and one or more
    consents can be given by each owner.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        uuid: A unique randomly generated UUID that identifies the smart home.
        name: A unique string that represents the name of the smart home.
        address: A string that represents the address of the smart home.
        owned_by_users: A list of `UserSmartHome` instances.
            Represents a one-to-many relationship with the `UserSmartHome` class.
        installed_applications: A list of `UserSmartHomeApplication` instances.
            Represents a one-to-many relationship with the `UserSmartHomeApplication` class.
        given_consents: A list of `UserSmartHomeAvailableConsent` instances.
            Represents a one-to-many relationship with the `UserSmartHomeAvailableConsent` class.
    """

    __tablename__ = "smart_homes"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    owned_by_users: Mapped[List["UserSmartHome"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    installed_applications: Mapped[List["UserSmartHomeApplication"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    given_consents: Mapped[List["UserSmartHomeAvailableConsent"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    rooms: Mapped[List["Room"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    devices: Mapped[List["Device"]] = relationship(  # noqa: F821 # type: ignore
        backref="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    rules: Mapped[List["DbRule"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )
    entities: Mapped[List["DbEntity"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="smart_home", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"SmartHome(id={self.id}, uuid={self.uuid}, name={self.name}, address={self.address})"
