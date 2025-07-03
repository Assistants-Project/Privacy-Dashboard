from sqlalchemy.orm import Mapped, mapped_column

from ...extensions import db


class TestObj(db.Model):
    """An example of a basic SQLAlchemy class, to be deleted later.

    Attributes:
        id: An auto-incremented integer identifier, used as the primary key.
        name: A unique string identifier for the object.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    def __repr__(self) -> str:
        return f"TestObj(id={self.id!r}, name={self.name!r})"
