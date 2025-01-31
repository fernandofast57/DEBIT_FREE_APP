
import pytest
from decimal import Decimal
from app.services.gold.weekly_distribution import WeeklyGoldDistribution

@pytest.mark.asyncio
async def test_gold_purchase_calculations():
    service = WeeklyGoldDistribution()
    test_cases = [
        {
            'purchase_amount': Decimal('877'),
            'fixing_price': Decimal('85.13'),
            'expected': {
                'structure_fee': Decimal('43.85'),
                'net_amount': Decimal('833.15'),
                'total_gold_grams': Decimal('9.7867'),
                'bonus_gold': Decimal('0.1664'),
                'client_gold': Decimal('9.6203')
            }
        },
        {
            'purchase_amount': Decimal('1000'),
            'fixing_price': Decimal('85.13'),
            'expected': {
                'structure_fee': Decimal('50'),
                'net_amount': Decimal('950'),
                'total_gold_grams': Decimal('11.1594'),
                'bonus_gold': Decimal('0.1897'),
                'client_gold': Decimal('10.9697')
            }
        }
    ]

    for case in test_cases:
        # Calculate structure fee
        structure_fee = case['purchase_amount'] * service.structure_fee
        assert structure_fee == case['expected']['structure_fee'], \
            f"Structure fee calculation failed for {case['purchase_amount']}€"

        # Calculate net amount after structure fee
        net_amount = case['purchase_amount'] - structure_fee
        assert net_amount == case['expected']['net_amount'], \
            f"Net amount calculation failed for {case['purchase_amount']}€"

        # Calculate total gold grams
        total_gold = net_amount / case['fixing_price']
        assert abs(total_gold - case['expected']['total_gold_grams']) < Decimal('0.0001'), \
            f"Total gold calculation failed for {case['purchase_amount']}€"

        # Calculate bonus gold (1.7% of total)
        bonus_gold = total_gold * Decimal('0.017')
        assert abs(bonus_gold - case['expected']['bonus_gold']) < Decimal('0.0001'), \
            f"Bonus gold calculation failed for {case['purchase_amount']}€"

        # Calculate client gold
        client_gold = total_gold - bonus_gold
        assert abs(client_gold - case['expected']['client_gold']) < Decimal('0.0001'), \
            f"Client gold calculation failed for {case['purchase_amount']}€"
