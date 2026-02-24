from ...extensions import ma


class ApplicationAndAvailableConsentUuidReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=True, allow_none=False)
    available_consent_uuid = ma.UUID(required=True, allow_none=False)
