from ...extensions import ma
from marshmallow import fields


class HomeResSchema(ma.Schema):

    uuid = fields.String(required=True)
    name = fields.String(required=True)
    address = fields.String(allow_none=True)
    zip_code = fields.String(allow_none=True)
    country = fields.String(allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    timezone = fields.String(allow_none=True)
    language = fields.String(allow_none=True)
