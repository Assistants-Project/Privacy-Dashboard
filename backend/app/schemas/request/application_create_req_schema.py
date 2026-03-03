from ...extensions import ma


class ApplicationCreateReqSchema(ma.Schema):
    id = ma.Str(required=True, allow_none=False)
    title = ma.Str(required=True, allow_none=False)
    description = ma.Str(required=False, allow_none=True)
    available_consents = ma.List(
        ma.Str(required=True, allow_none=False), required=False, allow_none=True
    )
