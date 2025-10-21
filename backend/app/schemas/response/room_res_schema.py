from marshmallow import fields

from ...extensions import ma


class RoomResSchema(ma.Schema):
    room_uuid = fields.String(required=True)
    name = fields.String(required=True)
    category = fields.String(allow_none=True)
