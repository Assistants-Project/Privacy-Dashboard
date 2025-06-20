import enum
from typing import List

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserRole(enum.Enum):
    DATA_SUBJECT = "DATA_SUBJECT"
    DATA_CONTROLLER = "DATA_CONTROLLER"
    DATA_PROTECTION_OFFICER = "DATA_PROTECTION_OFFICER"


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    firstname: Mapped[str]
    lastname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    role = mapped_column(Enum(UserRole, validate_strings=True), nullable=False)
    profile_picture: Mapped[str | None]

    smart_homes: Mapped[List["UserSmartHomeRelation"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    # TODO: consider adding methods for password hashing and checking with werkzeug.security
