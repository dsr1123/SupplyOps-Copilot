
import pytest
from optimizer.models import CostBreakdown

def test_total_is_sum_of_parts():
    costs = CostBreakdown(transfer=1, lane=2, expedite=3, delay=4)
    assert costs.total == 10

def test_total_with_decimal_costs():
    costs = CostBreakdown(transfer=0.1, lane=0.2, expedite=0, delay=0)
    assert costs.total == pytest.approx(0.3)
