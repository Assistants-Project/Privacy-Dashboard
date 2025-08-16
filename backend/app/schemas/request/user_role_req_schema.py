from ...extensions import ma
from ...models import UserRole


class UserRoleReqSchema(ma.Schema):
    role = ma.Enum(UserRole, by_value=True, required=True, allow_none=False)
