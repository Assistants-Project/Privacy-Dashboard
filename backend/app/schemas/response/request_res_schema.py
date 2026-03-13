from ...extensions import ma
from ...models import Request


class RequestSchema(ma.SQLAlchemyAutoSchema):
    selected_consents = ma.List(
        ma.Dict(
            keys=ma.String(),
            values=ma.Raw(allow_none=True),
        ),
        allow_none=True,
    )

    class Meta:
        model = Request
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = (
            "id",
            "data_subject_user_id",
            "application_id",
            "smart_home_uuid",
            "processing_context_id",
            "user_smart_home_application_relation_id",
        )


class RequestResSchema(ma.Schema):
    request = ma.Nested(RequestSchema)
    user_email = ma.Email()
    user_firstname = ma.Str(allow_none=True)
    user_lastname = ma.Str(allow_none=True)
    application_name = ma.Str()
    application_uuid = ma.UUID()
    processing_context_uuid = ma.UUID()
