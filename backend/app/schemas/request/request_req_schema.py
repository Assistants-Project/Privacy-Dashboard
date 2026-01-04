from ...extensions import ma
from ...models import RightType


class RequestReqSchema(ma.Schema):
    right_type = ma.Enum(RightType, by_value=True, required=True, allow_none=False)
    additional_information = ma.Str(required=True, allow_none=False)
    smart_home_uuid = ma.Str(required=True, allow_none=False)
    application_uuid = ma.UUID(required=True, allow_none=False)
