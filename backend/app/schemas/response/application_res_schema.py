from ...extensions import ma
from ...models import Application


class ApplicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Application
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id",)


class ApplicationResSchema(ma.Schema):
    application = ma.Nested(ApplicationSchema)
    installed_at = ma.DateTime()
