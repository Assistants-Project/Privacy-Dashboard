from typing import Any, Dict, List
from ..repositories import TestObjRepository
from ..schemas.response import TestObjResSchema

single = TestObjResSchema()
multiple = TestObjResSchema(many=True)

class TestObjService:
    @staticmethod
    def get_test_obj_by_id(id: int) -> Dict[str, Any]:
        return single.dump(TestObjRepository.get_by_id(id))
    
    @staticmethod
    def get_all_test_objs() -> List[Dict[str, Any]]:
        return multiple.dump(TestObjRepository.get_all())
