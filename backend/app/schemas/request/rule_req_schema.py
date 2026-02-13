from marshmallow import Schema, fields, EXCLUDE


class RuleDetailSchema(Schema):
    """Schema for rule detail (parameter)"""

    class Meta:
        unknown = EXCLUDE

    url = fields.Str(required=True)
    id = fields.Str(required=False)
    name = fields.Str(required=False)
    type = fields.Str(required=True)
    value = fields.Raw(allow_none=True)
    alternatives = fields.List(fields.Raw(), allow_none=True, dump_default=[])


class RuleTriggerSchema(Schema):
    """Schema for rule trigger"""

    class Meta:
        unknown = EXCLUDE

    url = fields.Str(required=True)
    details = fields.List(fields.Nested(RuleDetailSchema), dump_default=[])


class RuleActionSchema(Schema):
    """Schema for rule action"""

    class Meta:
        unknown = EXCLUDE

    url = fields.Str(required=True)
    details = fields.List(fields.Nested(RuleDetailSchema), dump_default=[])


class RuleRequestSchema(Schema):
    """Schema for creating/updating a rule"""

    class Meta:
        unknown = EXCLUDE

    trigger = fields.Nested(RuleTriggerSchema, required=True)
    action = fields.Nested(RuleActionSchema, required=True)
    effect = fields.Str(required=True)
    subject = fields.Str(allow_none=True)
    expirationDate = fields.Str(allow_none=True)


class RuleResponseSchema(Schema):
    """Schema for rule response"""

    class Meta:
        unknown = EXCLUDE

    db_id = fields.Int(required=True)
    type = fields.Str(required=True)
    trigger = fields.Nested(RuleTriggerSchema, required=True)
    action = fields.Nested(RuleActionSchema, required=True)
    effect = fields.Str(allow_none=True)
    subject = fields.Str(allow_none=True)
    timestamp = fields.DateTime(allow_none=True)
    expirationDate = fields.Str(attribute="expiration_date", allow_none=True)
