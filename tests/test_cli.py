import json
from pathlib import Path

from optimizer.cli import EXIT_INPUT_ERROR, EXIT_OK, main

ROOT = Path(__file__).resolve().parent.parent
SCENARIO = ROOT / "data" / "scenarios" / "supplier_delay_po1024.json"
DATA_DIR = ROOT / "data"


def test_cli_compares_three_methods(capsys):
    code = main(["--scenario", str(SCENARIO), "--data-dir", str(DATA_DIR)])
    out = capsys.readouterr().out
    report = json.loads(out)

    assert code == EXIT_OK
    methods = [r["method"] for r in report["results"]]
    assert len(methods) == 3
    mip = report["results"][-1]
    assert mip["status"] == "OPTIMAL"
    assert mip["valid"] is True


def test_cli_missing_scenario_returns_input_error(capsys):
    code = main(["--scenario", str(ROOT / "no_such_file.json"), "--data-dir", str(DATA_DIR)])
    captured = capsys.readouterr()

    assert code == EXIT_INPUT_ERROR
    assert captured.out == ""
    assert "error" in captured.err
