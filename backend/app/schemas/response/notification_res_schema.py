from ...extensions import ma


class NotificationResSchema(ma.Schema):
    id = ma.Integer()
    type = ma.String()
    sent_at = ma.DateTime()
    is_read = ma.Boolean()
    sender_email = ma.String(allow_none=True)
    application_name = ma.String(allow_none=True)
    application_uuid = ma.UUID(allow_none=True)
    request_uuid = ma.UUID(allow_none=True)
    processing_context_uuid = ma.UUID(allow_none=True)
    payload = ma.Dict(keys=ma.String(), values=ma.Raw(allow_none=True), allow_none=True)
