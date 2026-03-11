from ...extensions import ma


class RefreshResultResSchema(ma.Schema):
    message = ma.Str(required=True, allow_none=False)
    warnings = ma.List(ma.Str(required=True, allow_none=False), required=True, allow_none=False)
