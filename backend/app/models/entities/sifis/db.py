from typing import List, TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....extensions import db

if TYPE_CHECKING:
    from ..user import User
    from ..smart_home import SmartHome
    from ..device import Device


class DbRule(db.Model):
    """Rule stored in database"""

    __tablename__ = "dbrule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    smart_home_id: Mapped[int] = mapped_column(
        ForeignKey("smart_homes.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'sifis'
    effect: Mapped[str] = mapped_column(String(50), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )  # Unix timestamp in milliseconds
    rule_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=True)
    expiration_date: Mapped[str] = mapped_column(String(20), nullable=True)
    # If set, this rule is managed automatically as a consequence of a consent.
    consent_uuid: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    smart_home: Mapped["SmartHome"] = relationship("SmartHome", back_populates="rules")
    triggers: Mapped[List["DbTrigger"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )
    actions: Mapped[List["DbAction"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )


class DbTrigger(db.Model):
    """Trigger stored in database"""

    __tablename__ = "dbtrigger"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(
        ForeignKey("dbrule.id", ondelete="CASCADE"), nullable=False
    )
    rule: Mapped["DbRule"] = relationship(back_populates="triggers")
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    device_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("devices.device_id", ondelete="SET NULL"), nullable=True
    )
    device: Mapped["Device"] = relationship("Device")
    
    details: Mapped[List["DbDetail"]] = relationship(
        back_populates="trigger",
        cascade="all, delete-orphan",
        foreign_keys="[DbDetail.trigger_id]",
    )


class DbAction(db.Model):
    """Action stored in database"""

    __tablename__ = "dbaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(
        ForeignKey("dbrule.id", ondelete="CASCADE"), nullable=False
    )
    rule: Mapped["DbRule"] = relationship(back_populates="actions")
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    device_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("devices.device_id", ondelete="SET NULL"), nullable=True
    )
    device: Mapped["Device"] = relationship("Device")

    details: Mapped[List["DbDetail"]] = relationship(
        back_populates="action",
        cascade="all, delete-orphan",
        foreign_keys="[DbDetail.action_id]",
    )


class DbDetail(db.Model):
    """Detail/parameter stored in database"""

    __tablename__ = "dbdetail"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trigger_id: Mapped[int] = mapped_column(
        ForeignKey("dbtrigger.id", ondelete="CASCADE"), nullable=True
    )
    action_id: Mapped[int] = mapped_column(
        ForeignKey("dbaction.id", ondelete="CASCADE"), nullable=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'entity', 'location', etc.
    value: Mapped[str] = mapped_column(Text, nullable=True)
    value_url: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # valueURL in Java

    trigger: Mapped["DbTrigger"] = relationship(
        back_populates="details", foreign_keys=[trigger_id]
    )
    action: Mapped["DbAction"] = relationship(
        back_populates="details", foreign_keys=[action_id]
    )
