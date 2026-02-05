from ...extensions import ma


class PrivacyImpactAssessmentResSchema(ma.Schema):
    application_uuid = ma.UUID(required=True, allow_none=False)
    content = ma.Dict(required=True, allow_none=False)

