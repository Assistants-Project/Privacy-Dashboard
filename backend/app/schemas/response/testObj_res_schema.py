from ...extensions import ma
from ...models import TestObj

class TestObjResSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TestObj
