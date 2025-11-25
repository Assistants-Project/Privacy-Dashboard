from uuid import UUID

from flask_smorest import Blueprint

from ..models import Status
from ..schemas import (
    ApplicationAndUserUuidReqSchema,
    RequestHandlingReqSchema,
    RequestReqSchema,
    RequestResSchema,
    RequestSchema,
    RequestStatusReqSchema,
    RequestUuidReqSchema,
    SmartHomeUuidReqSchema,
)
from ..services import RequestService
from ..utils import dc_or_dpo_required, ds_required

request_bp = Blueprint(
    "Requests API",
    "request_bp",
    url_prefix="/api/requests",
    description="Endpoints for requests",
)


@request_bp.route("/application/<application_uuid>/user/<user_uuid>", methods=["GET"])
@request_bp.arguments(ApplicationAndUserUuidReqSchema, location="path", as_kwargs=True)
@request_bp.response(200, RequestResSchema(many=True))
@dc_or_dpo_required()
def get_requests_by_managed_application_uuid_and_user_uuid(
    application_uuid: UUID, user_uuid: UUID, current_user
):
    return (
        RequestService.get_requests_by_dc_or_dpo_id_and_application_uuid_and_user_uuid(
            current_user.id, application_uuid, user_uuid
        )
    )


@request_bp.route("/", methods=["GET"])
@request_bp.arguments(RequestStatusReqSchema, location="query", as_kwargs=True)
@request_bp.response(200, RequestResSchema(many=True))
@dc_or_dpo_required()
def get_requests(status: Status | None, current_user):
    return RequestService.get_requests_by_dc_or_dpo_id(current_user.id, status)


@request_bp.route("/home/<smart_home_uuid>", methods=["GET"])
@request_bp.arguments(SmartHomeUuidReqSchema, location="path", as_kwargs=True)
@request_bp.arguments(RequestStatusReqSchema, location="query", as_kwargs=True)
@request_bp.response(200, RequestResSchema(many=True))
@ds_required()
def get_requests_by_smart_home_uuid(
    smart_home_uuid: str, status: Status | None, current_user
):
    return RequestService.get_requests_by_ds_id_and_smart_home_uuid(
        current_user.id, smart_home_uuid, status
    )


@request_bp.route("/submit", methods=["POST"])
@request_bp.arguments(RequestReqSchema, location="json", as_kwargs=False)
@request_bp.response(201, RequestSchema)
@ds_required()
def submit_request(request, current_user):
    return RequestService.submit_request(current_user.id, request)


@request_bp.route("/handle/<request_uuid>", methods=["PUT"])
@request_bp.arguments(RequestUuidReqSchema, location="path", as_kwargs=True)
@request_bp.arguments(RequestHandlingReqSchema, location="json", as_kwargs=True)
@request_bp.response(200, RequestSchema)
@dc_or_dpo_required()
def handle_request(
    request_uuid: UUID, response: str | None, status: Status, current_user
):
    return RequestService.handle_request(
        current_user.id, request_uuid, response, status
    )
