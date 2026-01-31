from ...extensions import ma
from .message_res_schema import MessageResSchema
from .user_res_schema import UserResSchema


class UserMessageResSchema(ma.Schema):
    user = ma.Nested(UserResSchema, required=True)
    last_message = ma.Nested(MessageResSchema, required=True)
