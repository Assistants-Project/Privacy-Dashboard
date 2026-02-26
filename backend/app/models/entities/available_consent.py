from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class AvailableConsent(db.Model):
    """Model for an available consent mapped to the table `available_consents`.

    An `AvailableConsent` instance corresponds to one consent available for an application,
    which can be given or revoked by a Data Subject in a specific smart home for that application.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        uuid: A unique randomly generated UUID that identifies the available consent.
        content: A string that represents the content of the consent.
        application_id: A foreign key ID of the application which the available consent is associated to.
        application: An application which the available consent is associated to.
            Represents a many-to-one relationship with the `Application` class.
        given_by_user_smart_home_combinations: A list of `UserSmartHomeAvailableConsent` instances.
            Represents a one-to-many relationship with the `UserSmartHomeAvailableConsent` class.
    """

    __tablename__ = "available_consents"
    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "content",
            name="uq_available_consents_application_id_content",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    content: Mapped[str]
    # Optional mapping from this consent to a SIFIS action (stored as action id, e.g. sifis_all_video_actions).
    sifis_action_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE")
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        return f"AvailableConsent(id={self.id}, uuid={self.uuid!r}, content={self.content})"
