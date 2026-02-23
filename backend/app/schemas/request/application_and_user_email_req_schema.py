from marshmallow import validate

from ...extensions import ma


class ApplicationAndUserEmailReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=True, allow_none=False)
    user_email = ma.String(required=True, allow_none=False, validate=validate.Email())
