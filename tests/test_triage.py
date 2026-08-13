from __future__ import annotations

from pathlib import Path

from ai_log_triage_lab.triage import Category, Severity, classify, run


def test_classify_returns_structured_baseline() -> None:
    result = classify("Synthetic authentication token failed", "error")

    assert result["category"] == Category.ACCESS_OR_INTEGRATION
    assert result["severity"] == Severity.HIGH
    assert "credentials" in result["suggested_action"]


def test_run_evaluates_labeled_dataset(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    summary = run(root / "data" / "sample" / "synthetic_logs.jsonl", tmp_path / "triage.json")

    assert summary["logs"] == 5
    assert summary["evaluation"] == {"labeled_cases": 5, "correct_cases": 5, "accuracy": 1.0}
    assert (tmp_path / "triage.json").exists()
