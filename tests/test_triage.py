from __future__ import annotations

from pathlib import Path

import pytest

from ai_log_triage_lab.triage import Category, Severity, classify, evaluate, run


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


@pytest.mark.parametrize(
    ("message", "level", "category", "severity"),
    [
        ("Synthetic CSV load delayed", "warning", Category.DATA_PIPELINE, Severity.MEDIUM),
        ("Synthetic service health timeout", "error", Category.SYSTEM_HEALTH, Severity.HIGH),
        ("Synthetic queue delayed", "warning", Category.OPERATIONAL_DELAY, Severity.MEDIUM),
        ("Synthetic report completed", "info", Category.INFORMATIONAL, Severity.LOW),
    ],
)
def test_classify_known_categories(message: str, level: str, category: Category, severity: Severity) -> None:
    result = classify(message, level)

    assert result["category"] == category
    assert result["severity"] == severity


def test_evaluate_without_labels_returns_empty_score() -> None:
    assert evaluate([{"triage": {"category": "informational", "severity": "low"}}]) == {
        "labeled_cases": 0,
        "correct_cases": 0,
        "accuracy": None,
    }
