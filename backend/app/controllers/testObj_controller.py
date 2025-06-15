from flask import Blueprint, request, jsonify
from ..services import TestObjService

testObj_bp = Blueprint('testObj', __name__, url_prefix='/api/testObj')

@testObj_bp.route('/', methods=['GET'])
def get_all():
    test_objs = TestObjService.get_all_test_objs()
    test_objs_dict = [obj.to_dict() for obj in test_objs]
    return jsonify(test_objs_dict)

@testObj_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id: int):
    test_obj = TestObjService.get_test_obj_by_id(id)
    return jsonify(test_obj.to_dict())
