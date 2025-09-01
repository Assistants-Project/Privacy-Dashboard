import enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash

from ...extensions import db


class UserRole(enum.Enum):
    DATA_SUBJECT = "DATA_SUBJECT"
    DATA_CONTROLLER = "DATA_CONTROLLER"
    DATA_PROTECTION_OFFICER = "DATA_PROTECTION_OFFICER"


class User(db.Model):
    """Model for a user mapped to the table `users`.

    A `User` instance corresponds to a person that has an account of one of the three roles
    and uses the application accordingly.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        uuid: A unique randomly generated UUID that identifies the application.
        firstname: A string that represents the first name of the user.
        lastname: A string that represents the last name of the user.
        email: A unique string that represents the email address of the user.
        password_hash: A string that represents the hashed password of the user.
        role: An enum that represents the role of the user, one of
            `DATA_SUBJECT`, `DATA_CONTROLLER` and `DATA_PROTECTION_OFFICER`.
        profile_picture: An optional string that represents the path to the profile picture of the user, if any.
        owned_smart_homes: A list of `UserSmartHome` instances.
            Represents a one-to-many relationship with the `UserSmartHome` class.
        installed_applications: A list of `UserSmartHomeApplication` instances.
            Represents a one-to-many relationship with the `UserSmartHomeApplication` class.
        given_consents: A list of `UserSmartHomeAvailableConsent` instances.
            Represents a one-to-many relationship with the `UserSmartHomeAvailableConsent` class.
        sent_messages: A list of messages the user sent.
            Represents a one-to-many relationship with the `Message` class.
        received_messages: A list of messages the user received.
            Represents a one-to-many relationship with the `Message` class.
        sent_notifications: A list of notifications the user sent.
            Represents a one-to-many relationship with the `Notification` class.
        received_notifications: A list of `UserNotification` instances.
            Represents a one-to-many relationship with the `UserNotification` class.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    firstname: Mapped[str]
    lastname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    role = mapped_column(Enum(UserRole, validate_strings=True), nullable=False)
    profile_picture: Mapped[str | None]

    owned_smart_homes: Mapped[List["UserSmartHome"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    installed_applications: Mapped[List["UserSmartHomeApplication"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    given_consents: Mapped[List["UserSmartHomeAvailableConsent"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    sent_messages: Mapped[List["Message"]] = relationship(  # noqa: F821 # type: ignore
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    received_messages: Mapped[List["Message"]] = relationship(  # noqa: F821 # type: ignore
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sent_notifications: Mapped[List["Notification"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="sender", cascade="all, delete-orphan", passive_deletes=True
    )
    received_notifications: Mapped[List["UserNotification"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def check_password(self, password: str) -> bool:
        """Checks if the given password matches the stored password hash.

        Args:
            password: The password given by the user attempting to log in.

        Returns:
            True if the password matches the stored password hash, False otherwise.
        """

        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, uuid={self.uuid!r}, firstname={self.firstname!r}, lastname={self.lastname!r}, \
            email={self.email!r}, password_hash={self.password_hash!r}, role={self.role!r}), \
            profile_picture={self.profile_picture!r})"
