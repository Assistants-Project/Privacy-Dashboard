from flask_smorest import Blueprint

from ..schemas import HomeResSchema
from ..services.smartotum_service import SmartotumService
from ..utils import smartotum_required

homes_bp = Blueprint(
    "Homes API",
    "homes_bp",
    url_prefix="/api/homes",
    description="Integration of Smartotum homes",
)

@homes_bp.route("", methods=["GET"])
@homes_bp.response(200, HomeResSchema(many=True))
@smartotum_required()
def list_homes():
    return SmartotumService.get_homes()