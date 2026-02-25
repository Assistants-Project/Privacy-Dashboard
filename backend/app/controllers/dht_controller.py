from flask import jsonify, request
from flask_smorest import Blueprint

from ..integrations.smartotum.client import SmartotumClient
from ..services.home_service import SmartHomeService
from ..utils import ds_required


dht_bp = Blueprint(
    "DHT API",
    "dht_bp",
    url_prefix="/api/dht",
    description="Proxy endpoints for Smartotum DHT (testing uses local mocks, otherwise calls official DHT)",
)


def _get_bearer_token_from_request() -> str | None:
    token = request.cookies.get("st_access_token")
    if token:
        return token
    auth_header = request.headers.get("Authorization") or ""
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip() or None
    return None


@dht_bp.route("/homes/<home_uuid>/topic_name/<topic_name>", methods=["GET"])
@ds_required()
def list_topic_items(current_user, home_uuid: str, topic_name: str):
    SmartHomeService.verify_home_access(home_uuid, current_user)

    access_token = _get_bearer_token_from_request()
    if not access_token:
        return jsonify({"error": "Missing access token"}), 401

    client = SmartotumClient()
    items = client.get_dht_topic_items(access_token, home_uuid, topic_name)
    return jsonify(items), 200


@dht_bp.route("/homes/<home_uuid>/get_all", methods=["GET"])
@ds_required()
def get_all_items(current_user, home_uuid: str):
    SmartHomeService.verify_home_access(home_uuid, current_user)

    access_token = _get_bearer_token_from_request()
    if not access_token:
        return jsonify({"error": "Missing access token"}), 401

    client = SmartotumClient()
    items = client.get_dht_all_items(access_token, home_uuid)
    return jsonify(items), 200
