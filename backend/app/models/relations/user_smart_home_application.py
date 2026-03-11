from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class UserSmartHomeApplication(db.Model):
    """Association object representing the tri-directional many-to-many
    relationship between `User`, `SmartHome`, and `Application`,
    mapped to the table `user_smart_home_application_relations`.

    A `UserSmartHomeApplication` instance represents a unique combination
    of a `User` instance, a `SmartHome` instance, and an `Application`
    instance, and means that such user installed such application in such smart home.
    Only users with role `DATA_SUBJECT` can install an application in a smart home; Data Controllers
    and DPOs, who only manage applications, have their `smart_home_id`
    and `smart_home` attributes set to `None`.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        user_id: A foreign key ID of the Data Subject who installed the application in the smart home,
            or of the Data Controller or DPO who manages the application.
        smart_home_id: A foreign key ID of the smart home in which the application is installed by the Data Subject.
            Defaults to `None` for Data Controllers and DPOs.
        application_id: A foreign key ID of the application installed in the smart home by the Data Subject,
            or of the application managed by the Data Controller or DPO.
        installed_at: A datetime object that represents the date and time when the application
            was installed by the user, defaults to the current date and time.
        user: A Data Subject who installed the application in the smart home or a Data Controller or DPO
            who manages the application.
            Represents a many-to-one relationship with the `User` class.
        smart_home: A smart home in which the application is installed by the Data Subject. Defaults to `None`
            for Data Controllers and DPOs.
            Represents a many-to-one relationship with the `SmartHome` class.
        application: An application installed in the smart home by the Data Subject or managed by the Data Controller or DPO.
            Represents a many-to-one relationship with the `Application` class.
        submitted_requests: A list of requests submitted by the Data Subject in the smart home regarding the application.
            Represents a one-to-many relationship with the `Request` class.
    """

    __tablename__ = "user_smart_home_application_relations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    smart_home_id: Mapped[int | None] = mapped_column(
        ForeignKey("smart_homes.id", ondelete="CASCADE"), default=None
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    installed_at: Mapped[datetime] = mapped_column(default=datetime.now())

    user: Mapped["User"] = relationship(  # noqa: F821 # type: ignore
        back_populates="installed_applications"
    )
    smart_home: Mapped["SmartHome | None"] = relationship(  # noqa: F821 # type: ignore
        back_populates="installed_applications"
    )
    application: Mapped["Application"] = relationship(  # noqa: F821 # type: ignore
        back_populates="installed_by_user_smart_home_combinations"
    )
    # Requests are retained as audit records even if this relation is pruned.
    # The DB FK is configured as ON DELETE SET NULL.
    submitted_requests: Mapped[List["Request"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="user_smart_home_application_relation",
        passive_deletes=True,
    )

    __table_args__ = (UniqueConstraint("user_id", "smart_home_id", "application_id"),)

    def __repr__(self) -> str:
        return f"UserSmartHomeApplication(id={self.id}, user_id={self.user_id}, \
            smart_home_id={self.smart_home_id}, application_id={self.application_id}), \
            installed_at={self.installed_at})"
