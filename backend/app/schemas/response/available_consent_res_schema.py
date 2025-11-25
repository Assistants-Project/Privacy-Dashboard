from ...extensions import ma
from ...models import AvailableConsent


class AvailableConsentResSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AvailableConsent
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id",)
