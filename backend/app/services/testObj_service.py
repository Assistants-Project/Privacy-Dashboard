from ..repositories import TestObjRepository
from ..models import TestObj

class TestObjService:
    @staticmethod
    def get_test_obj_by_id(id: int) -> TestObj:
        return TestObjRepository.get_by_id(id)
    
    @staticmethod
    def get_all_test_objs() -> list:
        return TestObjRepository.get_all()
