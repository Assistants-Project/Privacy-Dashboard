from typing import List

from ..extensions import db
from ..models import TestObj


class TestObjRepository:
    @staticmethod
    def get_by_id(user_id: int) -> TestObj | None:
        return db.session.scalar(db.select(TestObj).filter_by(id=user_id))

    @staticmethod
    def get_all() -> List[TestObj]:
        return db.session.scalars(db.select(TestObj)).all()
