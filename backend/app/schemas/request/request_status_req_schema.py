from ...extensions import ma
from ...models import Status


class RequestStatusReqSchema(ma.Schema):
    status = ma.Enum(
        Status, by_value=True, required=False, allow_none=False, load_default=None
    )
