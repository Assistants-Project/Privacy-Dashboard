from flask_smorest import Blueprint, abort

from ..schemas.response import TestObjResSchema
from ..services import TestObjService

testObj_bp = Blueprint(
    "testObj", "testObj", url_prefix="/api/testObj", description="Test Objects API"
)


@testObj_bp.route("/", methods=["GET"])
@testObj_bp.response(200, TestObjResSchema(many=True))
def get_all():
    """Retrieve all test objects"""
    return TestObjService.get_all_test_objs()


@testObj_bp.route("/<int:id>", methods=["GET"])
@testObj_bp.response(200, TestObjResSchema)
def get_by_id(id: int):
    """Get a test object by its ID"""
    try:
        response = TestObjService.get_test_obj_by_id(id)
    except Exception as e:
        abort(404, message=str(e))
    return response
