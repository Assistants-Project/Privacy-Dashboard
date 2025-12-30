from ...extensions import ma


class MessageReqSchema(ma.Schema):
    content = ma.Str(required=True, allow_none=False)
    attachment = ma.Str(required=False)
    receiver_uuid = ma.UUID(required=True)
