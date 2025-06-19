from typing import List
from ..models import TestObj
from ..repositories import TestObjRepository

class TestObjService:
    @staticmethod
    def get_test_obj_by_id(id: int) -> TestObj:
        """Retrieve a test object by its ID from the database.

        :param int id: the ID of the test object to retrieve

        :return TestObj: the retrieved test object

        :raise Exception: if no test object with the given ID is found
        """
        testObj = TestObjRepository.get_by_id(id)
        if not testObj:
            raise Exception(f"TestObj with id {id} not found")
        return testObj
    
    @staticmethod
    def get_all_test_objs() -> List[TestObj]:
        """Retrieve all test objects from the database.

        :return List[TestObj]: the retrieved test objects
        """
        return TestObjRepository.get_all()
