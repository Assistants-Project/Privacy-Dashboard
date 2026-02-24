from ...extensions import ma
from ...models import AvailableConsent


class AvailableConsentResSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AvailableConsent
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id",)


class ConsentStateResSchema(ma.Schema):
    uuid = ma.UUID()
    content = ma.String()
    given = ma.Boolean()
    given_at = ma.DateTime(allow_none=True)
