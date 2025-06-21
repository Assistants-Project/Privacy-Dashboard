from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class AvailableConsent(db.Model):
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
