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


DOC_STATUS_VALUES = ("AVAILABLE", "MISSING")

class ManagedApplicationResSchema(ma.Schema):
    application = ma.Nested(ApplicationSchema, required=True)
    owner = ma.Nested(UserResSchema, required=True, allow_none=False)
    data_controllers = ma.List(ma.Nested(UserResSchema), required=True)
    dpo = ma.Nested(UserResSchema, required=True, allow_none=True)
    pn_status = ma.String(required=True, validate=validate.OneOf(DOC_STATUS_VALUES))
    pia_status = ma.String(required=True, validate=validate.OneOf(DOC_STATUS_VALUES))
    pending_right_requests_count = ma.Integer(required=True, validate=validate.Range(min=0))
    installed_at = ma.DateTime(required=False, allow_none=True)


class InstalledApplicationResSchema(ma.Schema):
    application = ma.Nested(ApplicationSchema, required=True)
    owner = ma.Nested(UserResSchema, required=True, allow_none=False)
    data_controllers = ma.List(ma.Nested(UserResSchema), required=True)
    dpo = ma.Nested(UserResSchema, required=True, allow_none=True)
    pn_status = ma.String(required=True, validate=validate.OneOf(DOC_STATUS_VALUES))
    pia_status = ma.String(required=True, validate=validate.OneOf(DOC_STATUS_VALUES))
    pending_right_requests_count = ma.Integer(required=True, validate=validate.Range(min=0))
    installed_at = ma.DateTime(required=True)
