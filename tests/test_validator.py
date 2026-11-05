from optimizer.heuristic import do_nothing, rule_based
from optimizer.validator import validate


def test_do_nothing_violates_vip_sla(tiny_problem):
    """If we don't ship any VIP orders, we violate the SLA."""
    solution = do_nothing(tiny_problem)
    result = validate(tiny_problem, solution)
    assert not result.is_valid
    assert any(v.check == "VIP SLA" for v in result.violations)


def test_rule_based_plan_is_valid(tiny_problem):
    """The rule-based heuristic should produce a valid plan."""
    solution = rule_based(tiny_problem)
    assert validate(tiny_problem, solution).is_valid
