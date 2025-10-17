from flask_smorest import Blueprint

from ..schemas import HomeResSchema
from ..schemas import DeviceResSchema
from ..services.smartotum_service import SmartotumService
from ..utils import smartotum_required
from ..utils import ds_required

homes_bp = Blueprint(
    "Homes API",
    "homes_bp",
    url_prefix="/api/homes",
    description="Integration of Smartotum homes",
)

@homes_bp.route("", methods=["GET"])
@homes_bp.response(200, HomeResSchema(many=True))
@ds_required()
def list_homes():
    return SmartotumService.get_homes()


@homes_bp.route("/<system_id>/devices", methods=["GET"])
@homes_bp.response(200, DeviceResSchema(many=True))
@ds_required()
def list_home_devices(system_id: str):
    return SmartotumService.get_home_devices(system_id)