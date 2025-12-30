from ...extensions import ma


class RequestUuidReqSchema(ma.Schema):
    request_uuid = ma.UUID(required=True, allow_none=False)
