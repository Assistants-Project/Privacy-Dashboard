from ...extensions import ma


class UserAndSmartHomeAndAvailableConsentUuidReqSchema(ma.Schema):
    user_uuid = ma.UUID(required=True, allow_none=False)
    smart_home_uuid = ma.Str(required=True, allow_none=False)
    available_consent_uuid = ma.UUID(required=True, allow_none=False)
