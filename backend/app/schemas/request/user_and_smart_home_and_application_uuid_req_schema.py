from ...extensions import ma


class UserAndSmartHomeAndApplicationUuidReqSchema(ma.Schema):
    user_uuid = ma.UUID(required=True, allow_none=False)
    smart_home_uuid = ma.Str(required=True, allow_none=False)
    application_uuid = ma.UUID(required=True, allow_none=False)
