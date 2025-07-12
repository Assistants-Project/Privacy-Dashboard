from ...extensions import ma


class AuthReqSchema(ma.Schema):
    email = ma.Email(required=True, allow_none=False)
    password = ma.String(required=True, allow_none=False)
