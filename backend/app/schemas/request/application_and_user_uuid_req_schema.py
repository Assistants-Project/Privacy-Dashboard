from ...extensions import ma


class ApplicationAndUserUuidReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=True, allow_none=False)
    user_uuid = ma.UUID(required=True, allow_none=False)
