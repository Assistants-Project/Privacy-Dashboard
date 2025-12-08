from ...extensions import ma


class PrivacyNoticeReqSchema(ma.Schema):
    content = ma.Str(required=True, allow_none=False)
