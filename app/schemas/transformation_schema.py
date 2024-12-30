
from marshmallow import Schema, fields, validate, ValidationError
from decimal import Decimal

class TransformationSchema(Schema):
    fixing_price = fields.Decimal(
        required=True,
        validate=validate.Range(min=Decimal('0.01'))
    )
    gold_grams = fields.Decimal(
        required=True,
        validate=validate.Range(min=Decimal('0.0001'))
    )
