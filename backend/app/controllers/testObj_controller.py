from flask import Blueprint, jsonify
from ..services import TestObjService

testObj_bp = Blueprint('testObj', __name__, url_prefix='/api/testObj')

@testObj_bp.route('/', methods=['GET'])
def get_all():
    return jsonify(TestObjService.get_all_test_objs())

@testObj_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id: int):
    return jsonify(TestObjService.get_test_obj_by_id(id))
