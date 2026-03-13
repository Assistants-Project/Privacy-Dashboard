from marshmallow import validate

from ...extensions import ma


class MarketplaceApplicationRegisterReqSchema(ma.Schema):
    id = ma.String(required=True, allow_none=False)
    name = ma.String(required=True, allow_none=False)
    description = ma.String(required=False, allow_none=True)
    owner_email = ma.String(
        required=True, allow_none=False, validate=validate.Email()
    )
    delegates_email = ma.List(
        ma.String(required=True, allow_none=False, validate=validate.Email()),
        required=False,
        allow_none=True,
    )
