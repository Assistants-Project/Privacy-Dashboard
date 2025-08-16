from ...extensions import ma


class ApplicationUuidReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=True, allow_none=False)
