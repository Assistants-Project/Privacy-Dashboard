from marshmallow import ValidationError, validates_schema

from ...extensions import ma


class MarketplaceApplicationPatchReqSchema(ma.Schema):
    title = ma.String(required=False, allow_none=False)
    description = ma.String(required=False, allow_none=True)

    @validates_schema
    def validate_payload(self, data, **kwargs):
        if "title" not in data and "description" not in data:
            raise ValidationError(
                "At least one of 'title' or 'description' must be provided."
            )
