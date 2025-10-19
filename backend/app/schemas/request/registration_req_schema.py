from ...extensions import ma
from marshmallow import fields
from ...models import UserRole

class RegistrationReqSchema(ma.Schema):
    email = fields.Email(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)
    role = fields.Enum( enum=UserRole, required=True, allow_none=False)
    firstname = fields.String(required=True, allow_none=False)
    lastname = fields.String(required=True, allow_none=False)

