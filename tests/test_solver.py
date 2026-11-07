from dataclasses import replace

import pytest
from ortools.linear_solver import pywraplp

from optimizer.models import SolveStatus
from optimizer.solver import solve
from optimizer.validator import validate


def test_tiny_problem_is_solved_optimally(tiny_problem):
    solution = solve(tiny_problem)
    assert solution.status is SolveStatus.OPTIMAL
    assert solution.cost_breakdown.total == pytest.approx(70)


def test_solver_output_passes_validator(tiny_problem):
    solution = solve(tiny_problem)
    assert validate(tiny_problem, solution).is_valid


def test_impossible_vip_order_is_infeasible(tiny_problem):
    o1, o2 = tiny_problem.orders
    problem = replace(tiny_problem, orders=[replace(o1, quantity=9999), o2])
    solution = solve(problem)
    assert solution.status is SolveStatus.INFEASIBLE


def test_unknown_priority_returns_error(tiny_problem):
    o1, o2 = tiny_problem.orders
    problem = replace(tiny_problem, orders=[replace(o1, priority="UNKNOWN"), o2])
    solution = solve(problem)
    assert solution.status is SolveStatus.ERROR
    assert "UNKNOWN" in solution.message


def test_no_solution_within_time_limit_is_timeout(monkeypatch, tiny_problem):
    monkeypatch.setattr(pywraplp.Solver, "Solve", lambda self: pywraplp.Solver.NOT_SOLVED)
    solution = solve(tiny_problem)
    assert solution.status is SolveStatus.TIMEOUT


def test_missing_solver_backend_is_error(monkeypatch, tiny_problem):
    monkeypatch.setattr(pywraplp.Solver, "CreateSolver", lambda name: None)
    solution = solve(tiny_problem)
    assert solution.status is SolveStatus.ERROR
    assert "SCIP" in solution.message

