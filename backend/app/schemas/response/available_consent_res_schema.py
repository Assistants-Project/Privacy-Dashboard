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
    # Optional mapping to a SIFIS action id (e.g. sifis_all_video_actions), used for automatic deny rules.
    sifis_action_id = ma.String(allow_none=True)
