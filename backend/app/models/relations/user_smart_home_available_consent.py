from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserSmartHomeAvailableConsent(db.Model):
    __tablename__ = "user_smart_home_available_consent_relations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    smart_home_id: Mapped[int] = mapped_column(
        ForeignKey("smart_homes.id", ondelete="CASCADE"), primary_key=True
    )
    available_consent_id: Mapped[int] = mapped_column(
        ForeignKey("available_consents.id", ondelete="CASCADE"), primary_key=True
    )
    given_at: Mapped[datetime] = mapped_column(default=datetime.now())

    user: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        back_populates="given_consents"
    )
    smart_home: Mapped["SmartHome"] = relationship(  # noqa: F821 # type: ignore
        back_populates="given_consents"
    )
    available_consent: Mapped["AvailableConsent"] = relationship(  # noqa: F821 # type: ignore
        back_populates="given_by_user_smart_home_combinations"
    )
