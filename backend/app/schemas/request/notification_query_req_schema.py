from marshmallow import validate

from ...extensions import ma


class NotificationQueryReqSchema(ma.Schema):
    only_unread = ma.Boolean(required=False, allow_none=False, load_default=False)
    limit = ma.Integer(required=False, allow_none=False, load_default=20, validate=validate.Range(min=1, max=100))
    offset = ma.Integer(required=False, allow_none=False, load_default=0, validate=validate.Range(min=0))
