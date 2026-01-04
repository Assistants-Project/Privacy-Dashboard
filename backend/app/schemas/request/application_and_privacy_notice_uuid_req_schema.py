from ...extensions import ma


class ApplicationAndPrivacyNoticeUuidReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=True, allow_none=False)
    privacy_notice_uuid = ma.UUID(required=True, allow_none=False)
