
from marshmallow import Schema, fields, validate, validates, ValidationError
from decimal import Decimal

class TransformationSchema(Schema):
    euro_amount = fields.Decimal(
        required=True, 
        validate=validate.Range(min=Decimal('100.00'), error="Minimum amount is 100 EUR")
    )
    fixing_price = fields.Decimal(required=True)
    
    @validates('fixing_price')
    def validate_fixing_price(self, value):
        if value <= 0:
            raise ValidationError("Fixing price must be greater than 0")
