from typing import List

from ..models import TestObj


class TestObjRepository:
    @staticmethod
    def get_by_id(user_id: int) -> TestObj | None:
        return TestObj.query.get(user_id)

    @staticmethod
    def get_all() -> List[TestObj]:
        return TestObj.query.all()
