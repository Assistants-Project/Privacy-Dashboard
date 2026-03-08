from marshmallow import ValidationError, validates_schema

from ...extensions import ma


class MarketplaceApplicationPatchReqSchema(ma.Schema):
    name = ma.String(required=False, allow_none=False)
    title = ma.String(required=False, allow_none=False)
    description = ma.String(required=False, allow_none=True)

    @validates_schema
    def validate_payload(self, data, **kwargs):
        if "name" not in data and "title" not in data and "description" not in data:
            raise ValidationError(
                "At least one of 'name', 'title' or 'description' must be provided."
            )
        if "name" in data and "title" in data:
            raise ValidationError("Provide only one of 'name' or 'title'.")
