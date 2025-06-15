from ..models import TestObj

class TestObjRepository:
    @staticmethod
    def get_by_id(user_id: int) -> TestObj:
        return TestObj.query.get(user_id)

    @staticmethod
    def get_all() -> list:
        return TestObj.query.all()
