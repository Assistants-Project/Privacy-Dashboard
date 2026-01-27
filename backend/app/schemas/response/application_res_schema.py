from ...extensions import ma
from ...models import Application
from .user_res_schema import UserResSchema 


class ApplicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Application
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id", "privacy_impact_assessment")


class ApplicationResSchema(ma.Schema):
    application = ma.Nested(ApplicationSchema)
    installed_at = ma.DateTime()

class ApplicationCatalogItemResSchema(ma.Schema):
    application = ma.Nested(ApplicationSchema, required=True)
    data_controllers = ma.List(ma.Nested(UserResSchema), required=True)
    dpo = ma.Nested(UserResSchema, required=True, allow_none=True)


class InstalledApplicationWithManagersResSchema(ma.Schema):
    application = ma.Nested(ApplicationSchema, required=True)
    installed_at = ma.DateTime(required=True)
    data_controllers = ma.List(ma.Nested(UserResSchema), required=True)
    dpo = ma.Nested(UserResSchema, required=True, allow_none=True)
