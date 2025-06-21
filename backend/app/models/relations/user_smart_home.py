from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserSmartHome(db.Model):
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
