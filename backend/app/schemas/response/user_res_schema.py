from ...extensions import ma
from ...models import User


class UserResSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id", "password_hash")
