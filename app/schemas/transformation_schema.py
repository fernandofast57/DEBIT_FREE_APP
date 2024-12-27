
from marshmallow import Schema, fields, validate

class TransformationSchema(Schema):
    euro_amount = fields.Decimal(required=True, validate=validate.Range(min=0))
    fixing_price = fields.Decimal(required=True)
