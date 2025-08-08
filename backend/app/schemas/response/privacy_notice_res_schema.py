from ...extensions import ma
from ...models import PrivacyNotice


class PrivacyNoticeResSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PrivacyNotice
        include_relationships = False
        load_instance = False
        exclude = ("id",)
