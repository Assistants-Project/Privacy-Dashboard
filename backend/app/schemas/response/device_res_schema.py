from marshmallow import fields

from ...extensions import ma
from ...models import Room


class DeviceResSchema(ma.Schema):
    device_uuid = fields.String(required=True)
    name = fields.String(required=True)
    topic_name = fields.String(allow_none=True)
    #room_uuid = fields.Method("_get_room_uuid")

    #can be used to get also the room
    # def _get_room_uuid(self, obj):
    #     if getattr(obj, "room_id", None) is None:
    #         return None
    #     room = Room.query.get(obj.room_id)
    #     return str(room.room_uuid) if room else None
