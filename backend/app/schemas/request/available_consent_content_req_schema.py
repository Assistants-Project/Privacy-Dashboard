from marshmallow import validate
from ...extensions import ma


class AvailableConsentContentReqSchema(ma.Schema):
    content = ma.String(required=True, allow_none=False, validate=validate.Length(min=1))
