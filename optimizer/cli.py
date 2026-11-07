"""Command-line entry point: compare Do Nothing / Rule-Based / MIP on one scenario."""
import argparse
from pathlib import Path
from typing import List, Optional
import json
from dataclasses import asdict
import sys
from optimizer.data_loader import DataValidationError, load_problem
from optimizer.heuristic import do_nothing, rule_based
from optimizer.solver import solve
from optimizer.models import Solution
from optimizer.validator import ValidationResult, validate
EXIT_OK = 0
EXIT_INPUT_ERROR = 3

METHODS = {
    "do_nothing": do_nothing,
    "rule_based": rule_based,
    "mip": solve,
}


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m optimizer.cli",
        description="Compare three planning methods on a disruption scenario.",
    )
    parser.add_argument("--scenario", type=Path, required=True,
                        help="path to scenario JSON file")
    parser.add_argument("--data-dir", type=Path, default=Path("data"),
                        help="directory with the CSV tables (default: data)")
    return parser.parse_args(argv)


def solution_to_dict(solution: Solution, check: ValidationResult) -> dict:
    cb = solution.cost_breakdown
    return {
        "method": solution.method,
        "status": solution.status.value,
        "valid": check.is_valid,
        "total_cost": round(cb.total, 2) if cb else None,
        "cost_breakdown": {k: round(v, 2) for k, v in asdict(cb).items()} if cb else None,
        "delayed_qty": sum(d.quantity for d in solution.delayed_orders),
        "violations": [asdict(v) for v in check.violations],
        "solve_time_seconds": round(solution.solve_time_seconds, 3),
        "message": solution.message,
        "plan": {
            "transfers": [asdict(t) for t in solution.transfers],
            "expedites": [asdict(e) for e in solution.expedites],
            "delayed_orders": [asdict(d) for d in solution.delayed_orders],
        },
    }


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        problem = load_problem(args.data_dir, args.scenario)
    except (FileNotFoundError, json.JSONDecodeError, DataValidationError) as e:
        print(f"error: cannot load input: {e}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    results = []
    for run in METHODS.values():
        solution = run(problem)
        results.append(solution_to_dict(solution, validate(problem, solution)))

    report = {"scenario": args.scenario.as_posix(), "results": results}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0



if __name__ == "__main__":
    raise SystemExit(main())