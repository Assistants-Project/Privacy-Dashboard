from ...extensions import ma
from ...models import Message


class MessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Message
        include_fk = False
        include_relationships = False
        load_instance = False
        exclude = ("id",)


class MessageResSchema(ma.Schema):
    message = ma.Nested(MessageSchema)
    sender_uuid = ma.UUID()
    receiver_uuid = ma.UUID()
