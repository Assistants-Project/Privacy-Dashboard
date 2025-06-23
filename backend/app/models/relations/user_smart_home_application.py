from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserSmartHomeApplication(db.Model):
    __tablename__ = "user_smart_home_application_relations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    smart_home_id: Mapped[int] = mapped_column(
        ForeignKey("smart_homes.id", ondelete="CASCADE"), nullable=False
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    installed_at: Mapped[datetime] = mapped_column(default=datetime.now())

    user: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        back_populates="installed_applications"
    )
    smart_home: Mapped["SmartHome"] = relationship(  # noqa: F821 # type: ignore
        back_populates="installed_applications"
    )
    application: Mapped["Application"] = relationship(  # noqa: F821 # type: ignore
        back_populates="installed_by_user_smart_home_combinations"
    )
    requests: Mapped[List["Request"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="user_smart_home_application_relation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (UniqueConstraint("user_id", "smart_home_id", "application_id"),)
