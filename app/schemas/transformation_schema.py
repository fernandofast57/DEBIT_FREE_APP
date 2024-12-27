
from marshmallow import Schema, fields, validate, validates, ValidationError
from decimal import Decimal

class TransformationSchema(Schema):
    """Schema for validating gold transformation input data."""
    euro_amount = fields.Decimal(
        required=True,
        validate=validate.Range(
            min=Decimal('100.00'),
            error="The minimum transformation amount is 100 EUR."
        )
    )
    fixing_price = fields.Decimal(
        required=True,
        validate=validate.Range(
            min=Decimal('0.01'),
            error="Fixing price must be greater than 0."
        )
    )
    fee_amount = fields.Decimal(
        required=True,
        validate=validate.Range(
            min=Decimal('0.01'),
            error="Fee amount must be greater than 0."
        )
    )
    gold_grams = fields.Decimal(
        required=True,
        validate=validate.Range(
            min=Decimal('0.0001'),
            error="Gold grams must be greater than 0."
        )
    )

    @validates('euro_amount')
    def validate_euro_amount(self, value):
        if value < Decimal('100.00'):
            raise ValidationError("Euro amount cannot be less than 100 EUR.")

    @validates('fixing_price')
    def validate_fixing_price(self, value):
        if value <= Decimal('0.0'):
            raise ValidationError("Fixing price must be a positive value.")

    @validates('fee_amount')
    def validate_fee_amount(self, value):
        if value <= Decimal('0.0'):
            raise ValidationError("Fee amount must be a positive value.")

    @validates('gold_grams')
    def validate_gold_grams(self, value):
        if value <= Decimal('0.0'):
            raise ValidationError("Gold grams must be a positive value.")
