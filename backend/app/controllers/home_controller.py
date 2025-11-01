from flask_smorest import Blueprint

from ..schemas import HomeResSchema
from ..schemas import DeviceResSchema
from ..schemas import RoomResSchema
from ..services.home_service import SmartHomeService
from ..utils import ds_required

homes_bp = Blueprint(
    "Homes API",
    "homes_bp",
    url_prefix="/api/homes",
    description="Endpoints for the homes of the user",
)

@homes_bp.route("", methods=["GET"])
@homes_bp.response(200, HomeResSchema(many=True))
@ds_required()
def list_homes(current_user):
    return SmartHomeService.get_homes(current_user)


@homes_bp.route("/refresh", methods=["POST"])
@homes_bp.response(202, description="Refresh started")
@ds_required()
def refresh_homes(current_user):
    SmartHomeService.update_database_for_user(current_user)
    return "", 202

@homes_bp.route("/<system_uuid>/rooms", methods=["GET"])
@homes_bp.response(200, RoomResSchema(many=True))
@ds_required()
def list_home_rooms(system_uuid: str, current_user):
    return SmartHomeService.get_home_rooms(system_uuid, current_user)

@homes_bp.route("/<system_uuid>/devices", methods=["GET"])
@homes_bp.response(200, DeviceResSchema(many=True))
@ds_required()
def list_home_devices(system_uuid: str, current_user):
    return SmartHomeService.get_home_devices(system_uuid, current_user)

@homes_bp.route("/<system_uuid>/rooms/<room_uuid>/devices", methods=["GET"])
@homes_bp.response(200, DeviceResSchema(many=True))
@ds_required()
def list_home_room_devices(system_uuid: str, room_uuid: str, current_user):
    return SmartHomeService.get_home_room_devices(system_uuid,room_uuid,current_user)