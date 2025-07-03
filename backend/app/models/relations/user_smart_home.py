from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserSmartHome(db.Model):
    """Association object representing the bi-directional many-to-many
    relationship between `User` and `SmartHome`, mapped to the table `user_smart_home_relations`.

    A `UserSmartHome` instance represents a unique combination of a
    `User` instance and a `SmartHome` instance, and means that such user owns such smart home.
    Only users with role `DATA_SUBJECT` can own a smart home.

    Attributes:
        user_id: A foreign key ID of the Data Subject who owns the smart home.
        smart_home_id: A foreign key ID of the smart home owned by the Data Subject.
        user: A Data Subject who owns the smart home.
            Represents a many-to-one relationship with the `User` class.
        smart_home: A smart home owned by the Data Subject.
            Represents a many-to-one relationship with the `SmartHome` class.
    """

    __tablename__ = "user_smart_home_relations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    smart_home_id: Mapped[int] = mapped_column(
        ForeignKey("smart_homes.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        back_populates="owned_smart_homes"
    )
    smart_home: Mapped["SmartHome"] = relationship(  # noqa: F821 # type: ignore
        back_populates="owned_by_users"
    )

    def __repr__(self) -> str:
        return f"UserSmartHome(user_id={self.user_id}, \
            smart_home_id={self.smart_home_id})"
