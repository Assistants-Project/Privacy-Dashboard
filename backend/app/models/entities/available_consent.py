from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class AvailableConsent(db.Model):
    """Model for an available consent mapped to the table `available_consents`.

    An `AvailableConsent` instance corresponds to one consent available for an application,
    which can be given or revoked by a Data Subject in a specific smart home for that application.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        content: A string that represents the content of the consent.
        application_id: A foreign key ID of the application which the available consent is associated to.
        application: An application which the available consent is associated to.
            Represents a many-to-one relationship with the `Application` class.
        given_by_user_smart_home_combinations: A list of `UserSmartHomeAvailableConsent` instances.
            Represents a one-to-many relationship with the `UserSmartHomeAvailableConsent` class.
    """

    __tablename__ = "available_consents"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE")
    )

    application: Mapped["Application"] = relationship(  # noqa: F821 # type: ignore
        back_populates="available_consents"
    )
    given_by_user_smart_home_combinations: Mapped[
        List["UserSmartHomeAvailableConsent"]  # noqa: F821 # type: ignore
    ] = relationship(
        back_populates="available_consent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"AvailableConsent(id={self.id}, content={self.content})"
