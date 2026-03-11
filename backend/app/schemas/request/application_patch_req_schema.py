from ...extensions import ma


class ApplicationPatchReqSchema(ma.Schema):
    title = ma.Str(required=True, allow_none=False)
    description = ma.Str(required=False, allow_none=True)
