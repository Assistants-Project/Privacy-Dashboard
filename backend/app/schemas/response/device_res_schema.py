from marshmallow import fields

from ...extensions import ma
#from ...models import Room


class DeviceResSchema(ma.Schema):
    device_uuid = fields.String(required=True)
    name = fields.String(required=True)
    topic_name = fields.String(allow_none=True)
    room_uuid = fields.Function(
    lambda obj: str(obj.room.room_uuid) if getattr(obj, "room", None) else None,
    allow_none=True,
    )
