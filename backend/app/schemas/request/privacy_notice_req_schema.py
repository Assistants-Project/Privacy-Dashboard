from ...extensions import ma


class PrivacyNoticeReqSchema(ma.Schema):
    application_uuid = ma.UUID(required=True, allow_none=False)
