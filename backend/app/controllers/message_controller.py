from uuid import UUID

#from flask_jwt_extended import current_user
from flask_smorest import Blueprint

from ..exceptions import WrongUserUuidException
from ..schemas import MessageResSchema, UserUuidReqSchema
from ..services import MessageService
from ..utils import dc_or_dpo_required, smartotum_required

from flask import g

message_bp = Blueprint(
    "Messages API",
    "message_bp",
    url_prefix="/api/messages",
    description="Endpoints for messages",
)


@message_bp.route("/history/<user_uuid>", methods=["GET"])
@message_bp.arguments(UserUuidReqSchema, location="path", as_kwargs=True)
@message_bp.response(200, MessageResSchema(many=True))

@smartotum_required()
@dc_or_dpo_required()
def get_messages_by_user_uuid(user_uuid: UUID):
    if user_uuid == g.current_user.uuid:
        raise WrongUserUuidException("Cannot get message history with yourself!")
    return MessageService.get_messages_by_dc_or_dpo_id_and_user_uuid(
        g.current_user.id, user_uuid
    )
