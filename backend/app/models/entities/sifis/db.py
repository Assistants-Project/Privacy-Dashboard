from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....extensions import db

if TYPE_CHECKING:
    from ..user import User


class DbEntity(db.Model):
    """IoT Entity stored in database"""

    __tablename__ = "dbentity"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User")
    triggers: Mapped[List["DbTrigger"]] = relationship(back_populates="entity")
    actions: Mapped[List["DbAction"]] = relationship(back_populates="entity")


class DbRule(db.Model):
    """Rule stored in database"""

    __tablename__ = "dbrule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'sifis'
    effect: Mapped[str] = mapped_column(String(50), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )  # Unix timestamp in milliseconds

    user: Mapped["User"] = relationship("User")
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
    rule_id: Mapped[int] = mapped_column(ForeignKey("dbrule.id"), nullable=False)
    entity_id: Mapped[int] = mapped_column(ForeignKey("dbentity.id"), nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    rule: Mapped["DbRule"] = relationship(back_populates="triggers")
    entity: Mapped["DbEntity"] = relationship(back_populates="triggers")
    details: Mapped[List["DbDetail"]] = relationship(
        back_populates="trigger",
        cascade="all, delete-orphan",
        foreign_keys="[DbDetail.trigger_id]",
    )


class DbAction(db.Model):
    """Action stored in database"""

    __tablename__ = "dbaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("dbrule.id"), nullable=False)
    entity_id: Mapped[int] = mapped_column(ForeignKey("dbentity.id"), nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    rule: Mapped["DbRule"] = relationship(back_populates="actions")
    entity: Mapped["DbEntity"] = relationship(back_populates="actions")
    details: Mapped[List["DbDetail"]] = relationship(
        back_populates="action",
        cascade="all, delete-orphan",
        foreign_keys="[DbDetail.action_id]",
    )


class DbDetail(db.Model):
    """Detail/parameter stored in database"""

    __tablename__ = "dbdetail"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trigger_id: Mapped[int] = mapped_column(ForeignKey("dbtrigger.id"), nullable=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("dbaction.id"), nullable=True)
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
