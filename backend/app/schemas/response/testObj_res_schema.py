from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ...models import TestObj

class TestObjResSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TestObj
