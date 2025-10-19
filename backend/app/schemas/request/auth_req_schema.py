from ...extensions import ma
from marshmallow import fields


class AuthReqSchema(ma.Schema):
    email = fields.Email(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)