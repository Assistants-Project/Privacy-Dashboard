from ...extensions import ma


class OptionalApplicationUuidReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=False, allow_none=True)
