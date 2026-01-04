from uuid import UUID

from flask_smorest import Blueprint

from ..exceptions import WrongUserUuidException
from ..schemas import MessageReqSchema, MessageResSchema, UserUuidReqSchema
from ..services import MessageService
from ..utils import logged_in_required

message_bp = Blueprint(
    "Messages API",
    "message_bp",
    url_prefix="/api/messages",
    description="Endpoints for messages",
)


@message_bp.route("/history/<user_uuid>", methods=["GET"])
@message_bp.arguments(UserUuidReqSchema, location="path", as_kwargs=True)
@message_bp.response(200, MessageResSchema(many=True))
@logged_in_required()
def get_messages_by_user_uuid(user_uuid: UUID, current_user):
    if user_uuid == current_user.uuid:
        raise WrongUserUuidException("Cannot get message history with yourself!")
    return MessageService.get_messages_by_user_id_and_user_uuid(
        current_user.id, current_user.role, user_uuid
    )


@message_bp.route("/send", methods=["POST"])
@message_bp.arguments(MessageReqSchema, location="json", as_kwargs=False)
@message_bp.response(201, MessageResSchema)
@logged_in_required()
def send_message(message, current_user):
    if message["receiver_uuid"] == current_user.uuid:
        raise WrongUserUuidException("Cannot send a message to yourself!")
    return MessageService.send_message(current_user.id, current_user.role, message)
