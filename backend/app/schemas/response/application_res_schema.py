from ...extensions import ma
from ...models import Application
from .user_res_schema import UserResSchema 
from marshmallow import validate


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

DOC_STATUS_VALUES = ("AVAILABLE", "MISSING", "FORBIDDEN")

class ApplicationWithManagersBaseResSchema(ma.Schema):
    application = ma.Nested(ApplicationSchema, required=True)
    data_controllers = ma.List(ma.Nested(UserResSchema), required=True)
    dpo = ma.Nested(UserResSchema, required=True, allow_none=True)
    pn_status = ma.String(required=True, validate=validate.OneOf(DOC_STATUS_VALUES))
    pia_status = ma.String(required=True, validate=validate.OneOf(DOC_STATUS_VALUES))


class ApplicationCatalogItemResSchema(ApplicationWithManagersBaseResSchema):
    pass

class InstalledApplicationWithManagersResSchema(ApplicationWithManagersBaseResSchema):
    installed_at = ma.DateTime(required=True)
