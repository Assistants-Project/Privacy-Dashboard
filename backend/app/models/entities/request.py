import enum

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class RightType(enum.Enum):
    ACCESS_DATA = "ACCESS_DATA"
    ASK_INFORMATION = "ASK_INFORMATION"
    COMPILE_COMPLAINT = "COMPILE_COMPLAINT"
    ERASE_DATA = "ERASE_DATA"
    REMOVE_EVERYTHING = "REMOVE_EVERYTHING"
    WITHDRAW_CONSENT = "WITHDRAW_CONSENT"


class Status(enum.Enum):
    PENDING = "PENDING"
    HANDLED = "HANDLED"


class Request(db.Model):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    right_type = mapped_column(Enum(RightType, validate_strings=True), nullable=False)
    addtional_information = mapped_column(Text, nullable=False)
    response = mapped_column(Text, nullable=True)
    status = mapped_column(
        Enum(Status, validate_strings=True), default=Status.PENDING, nullable=False
    )
    user_smart_home_application_relation_id: Mapped[int] = mapped_column(
        ForeignKey("user_smart_home_application_relations.id", ondelete="CASCADE")
    )

    user_smart_home_application_relation: Mapped["UserSmartHomeApplication"] = (  # noqa: F821 # type: ignore
        relationship(back_populates="requests")
    )
