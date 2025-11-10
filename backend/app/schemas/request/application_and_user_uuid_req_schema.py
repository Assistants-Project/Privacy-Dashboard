from ...extensions import ma


class ApplicationAndUserUuidReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=True)
    user_uuid = ma.UUID(required=True)
