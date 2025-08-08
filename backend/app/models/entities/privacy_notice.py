from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class PrivacyNotice(db.Model):
    """Model for a privacy notice mapped to the table `privacy_notices`.

    A `PrivacyNotice` instance corresponds to one privacy notice written by a Data Controller
    and associated to one or more applications.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        uuid: A unique randomly generated UUID that identifies the privacy notice.
        content: A text field that represents the content of the privacy notice.
        applications: A list of applications the privacy notice is associated to.
            Represents a one-to-many relationship with the `Application` class.
    """

    __tablename__ = "privacy_notices"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    content = mapped_column(Text, nullable=False)

    applications: Mapped[List["Application"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="privacy_notice", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"PrivacyNotice(id={self.id}, uuid={self.uuid!r}, \
            content={self.content})"
