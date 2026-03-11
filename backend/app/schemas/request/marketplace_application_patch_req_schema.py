from marshmallow import ValidationError, validates_schema

from ...extensions import ma


class MarketplaceApplicationPatchReqSchema(ma.Schema):
    title = ma.String(required=False, allow_none=False)
    description = ma.String(required=False, allow_none=True)
    available_consents = ma.List(
        ma.String(required=True, allow_none=False),
        required=False,
        allow_none=False,
    )

    @validates_schema
    def validate_payload(self, data, **kwargs):
        if (
            "title" not in data
            and "description" not in data
            and "available_consents" not in data
        ):
            raise ValidationError(
                "At least one of 'title', 'description' or 'available_consents' must be provided."
            )
