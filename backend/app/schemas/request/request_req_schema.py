from ...extensions import ma
from ...models import RightType


class RequestReqSchema(ma.Schema):
    right_type = ma.Enum(RightType, by_value=True, required=True, allow_none=False)
    additional_information = ma.Str(required=True, allow_none=False)
    selected_consents = ma.List(
        ma.UUID(required=True, allow_none=False), required=False, allow_none=True
    )
    smart_home_uuid = ma.Str(required=True, allow_none=False)
    application_uuid = ma.UUID(required=True, allow_none=False)
