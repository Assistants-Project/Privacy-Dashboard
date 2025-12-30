from ...extensions import ma
from ...models import AvailableConsent


class AvailableConsentResSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AvailableConsent
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id",)


class AvailableConsentGivenResSchema(ma.Schema):
    available_consent = ma.Nested(AvailableConsentResSchema)
    application_name = ma.Str()
    given_at = ma.DateTime()
