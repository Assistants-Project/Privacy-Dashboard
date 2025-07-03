from typing import List

from ..models import TestObj
from ..repositories import TestObjRepository


class TestObjService:
    @staticmethod
    def get_test_obj_by_id(id: int) -> TestObj:
        """Returns a test object fetched by its ID from the database.

        Args:
            id: The ID of the test object to retrieve.

        Raises:
            Exception: If no test object with the given ID is found in the database.
        """
        testObj = TestObjRepository.get_by_id(id)
        if not testObj:
            raise Exception(f"TestObj with id {id} not found")
        return testObj

    @staticmethod
    def get_all_test_objs() -> List[TestObj]:
        """Returns all test objects fetched from the database."""
        return TestObjRepository.get_all()
