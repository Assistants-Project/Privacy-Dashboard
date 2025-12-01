from ...extensions import ma


class AvailableConsentsReqSchema(ma.Schema):
    selected_consents = ma.List(
        ma.UUID(required=True, allow_none=False), required=True, allow_none=False
    )
