from ...extensions import ma


class ApplicationCreateReqSchema(ma.Schema):
    name = ma.Str(required=True, allow_none=False)
    description = ma.Str(required=False, allow_none=True)
    available_consents = ma.List(
        ma.Str(required=True, allow_none=False), required=False, allow_none=True
    )
