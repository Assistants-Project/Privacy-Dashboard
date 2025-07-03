from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserSmartHomeAvailableConsent(db.Model):
    """Association object representing the tri-directional many-to-many
    relationship between `User`, `SmartHome`, and `AvailableConsent`,
    mapped to the table `user_smart_home_available_consent_relations`.

    A `UserSmartHomeAvailableConsent` instance represents a unique combination
    of a `User` instance, a `SmartHome` instance, and an `AvailableConsent`
    instance, and means that such user gave such consent in such smart home.
    Only users with role `DATA_SUBJECT` can give consents.

    Attributes:
        user_id: A foreign key ID of the Data Subject who gave the consent in the smart home.
        smart_home_id: A foreign key ID of the smart home in which the consent was given by the Data Subject.
        available_consent_id: A foreign key ID of the consent given in the smart home by the Data Subject.
        given_at: A datetime object that represents the date and time when the consent was given
            in the smart home by the Data Subject, defaults to the current date and time.
        user: A Data Subject who gave the consent in the smart home.
            Represents a many-to-one relationship with the `User` class.
        smart_home: A smart home in which the consent was given by the Data Subject.
            Represents a many-to-one relationship with the `SmartHome` class.
        available_consent: An available consent given in the smart home by the Data Subject.
            Represents a many-to-one relationship with the `AvailableConsent` class.
    """

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

    def __repr__(self) -> str:
        return f"UserSmartHomeAvailableConsent(user_id={self.user_id}, smart_home_id={self.smart_home_id}, \
            available_consent_id={self.available_consent_id}, given_at={self.given_at})"
