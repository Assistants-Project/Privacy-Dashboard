from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db

class TestObj(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
