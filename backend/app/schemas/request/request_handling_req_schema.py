from ...extensions import ma
from ...models import Status


class RequestHandlingReqSchema(ma.Schema):
    response = ma.Str(required=False, allow_none=False)
    status = ma.Enum(Status, by_value=True, required=True, allow_none=False)
