from ...extensions import ma


class PrivacyImpactAssessmentReqSchema(ma.Schema):
    content = ma.Dict(required=True, allow_none=False)

