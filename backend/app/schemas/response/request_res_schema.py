from ...extensions import ma
from ...models import Request


class RequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Request
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id",)


class RequestResSchema(ma.Schema):
    request = ma.Nested(RequestSchema)
    user_email = ma.Email()
    application_name = ma.Str()
    application_uuid = ma.UUID()
