from ...extensions import ma


class SmartHomeAndApplicationUuidReqSchema(ma.Schema):
    smart_home_uuid = ma.Str(required=True, allow_none=False)
    application_uuid = ma.UUID(required=True, allow_none=False)
