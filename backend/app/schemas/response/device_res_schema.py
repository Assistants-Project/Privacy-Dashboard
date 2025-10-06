from marshmallow import fields

from ...extensions import ma


class DeviceResSchema(ma.Schema):
    id = fields.String(required=True)
    type = fields.String(required=True)
    current_system_id = fields.String(allow_none=True)
    node_id = fields.Integer(required=True)
    additional_data = fields.Dict(required=True)