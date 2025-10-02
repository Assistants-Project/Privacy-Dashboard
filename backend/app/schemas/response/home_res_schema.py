from ...extensions import ma


class HomeResSchema(ma.Schema):

    uuid = ma.String(required=True)
    name = ma.String(required=True)
    address = ma.String(allow_none=True)
    zip_code = ma.String(allow_none=True)
    country = ma.String(allow_none=True)
    latitude = ma.Float(allow_none=True)
    longitude = ma.Float(allow_none=True)
    timezone = ma.String(allow_none=True)
    language = ma.String(allow_none=True)
