from ...extensions import ma


class SmartHomeUuidReqSchema(ma.Schema):
    smart_home_uuid = ma.Str(required=True, allow_none=False)
