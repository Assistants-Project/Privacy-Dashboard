from typing import List

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db


class PrivacyNotice(db.Model):
    __tablename__ = "privacy_notices"

    id: Mapped[int] = mapped_column(primary_key=True)
    content = mapped_column(Text, nullable=False)

    applications: Mapped[List["Application"]] = relationship(  # noqa: F821 # type: ignore
        back_populates="privacy_notice", passive_deletes=True
    )
