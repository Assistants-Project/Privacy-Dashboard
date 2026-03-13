from ...extensions import ma
from .user_res_schema import UserResSchema


class ContactApplicationResSchema(ma.Schema):
    uuid = ma.UUID(required=True)
    name = ma.String(required=True)
    title = ma.String(required=True)


class ContactResSchema(ma.Schema):
    user = ma.Nested(UserResSchema, required=True)
    related_applications = ma.List(ma.Nested(ContactApplicationResSchema), required=True)
