from marshmallow import ValidationError, validates_schema

from ...extensions import ma


class CurrentUserPatchReqSchema(ma.Schema):
    current_password = ma.String(required=True, allow_none=False)
    email = ma.Email(required=False, allow_none=False)
    new_password = ma.String(required=False, allow_none=False)

    @validates_schema
    def validate_payload(self, data, **kwargs):
        if "email" not in data and "new_password" not in data:
            raise ValidationError(
                "At least one of 'email' or 'new_password' must be provided."
            )
