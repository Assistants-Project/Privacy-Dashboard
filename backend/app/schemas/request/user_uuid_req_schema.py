from ...extensions import ma


class UserUuidReqSchema(ma.Schema):
    user_uuid = ma.UUID(required=True, allow_none=False)
