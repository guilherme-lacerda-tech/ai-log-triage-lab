from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Category(StrEnum):
    ACCESS_OR_INTEGRATION = "access_or_integration"
    OPERATIONAL_DELAY = "operational_delay"
    DATA_PIPELINE = "data_pipeline"
    SYSTEM_HEALTH = "system_health"
    INFORMATIONAL = "informational"


class SuggestedAction(StrEnum):
    REVIEW_CREDENTIALS = "review synthetic connector credentials and retry policy"
    CHECK_QUEUE = "check recent synthetic events and queue status"
    INSPECT_PIPELINE = "inspect synthetic data pipeline inputs and database load"
    CHECK_HEALTH = "check synthetic service health and recent errors"
    NO_ACTION = "no immediate action"


@dataclass(frozen=True)
class LogEntry:
    log_id: str
    message: str
    level: str
    expected_category: str | None = None
    expected_severity: str | None = None


@dataclass(frozen=True)
class TriageResult:
    category: Category
    severity: Severity
    suggested_action: SuggestedAction
    explanation: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        return {key: str(value) for key, value in payload.items()}


def classify_entry(entry: LogEntry) -> TriageResult:
    return classify_result(entry.message, entry.level)


def classify_result(message: str, level: str) -> TriageResult:
    text = message.lower()
    if "authentication" in text or "credential" in text or "token" in text:
        category = Category.ACCESS_OR_INTEGRATION
        severity = Severity.HIGH
        action = SuggestedAction.REVIEW_CREDENTIALS
    elif "database" in text or "etl" in text or "csv" in text or "load" in text:
        category = Category.DATA_PIPELINE
        severity = Severity.HIGH if level == "error" else Severity.MEDIUM
        action = SuggestedAction.INSPECT_PIPELINE
    elif "timeout" in text or "offline" in text or "health" in text:
        category = Category.SYSTEM_HEALTH
        severity = Severity.HIGH if level == "error" else Severity.MEDIUM
        action = SuggestedAction.CHECK_HEALTH
    elif "delayed" in text or "queue" in text or level == "warning":
        category = Category.OPERATIONAL_DELAY
        severity = Severity.MEDIUM
        action = SuggestedAction.CHECK_QUEUE
    else:
        category = Category.INFORMATIONAL
        severity = Severity.LOW
        action = SuggestedAction.NO_ACTION
    return TriageResult(
        category=category,
        severity=severity,
        suggested_action=action,
        explanation=f"Matched deterministic baseline for {category.value}.",
    )


def classify(message: str, level: str) -> dict:
    return classify_result(message, level).to_dict()


def load_entries(logs_path: Path) -> list[LogEntry]:
    entries = []
    for line in logs_path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        entries.append(LogEntry(**item))
    return entries


def evaluate(results: list[dict]) -> dict:
    labeled = [item for item in results if item.get("expected_category") and item.get("expected_severity")]
    if not labeled:
        return {"labeled_cases": 0, "correct_cases": 0, "accuracy": None}
    correct = sum(
        1
        for item in labeled
        if item["triage"]["category"] == item["expected_category"] and item["triage"]["severity"] == item["expected_severity"]
    )
    return {"labeled_cases": len(labeled), "correct_cases": correct, "accuracy": round(correct / len(labeled), 2)}


def run(logs_path: Path, output_path: Path) -> dict:
    results = []
    for entry in load_entries(logs_path):
        item = asdict(entry)
        results.append({**item, "triage": classify_entry(entry).to_dict()})
    summary = {"logs": len(results), "evaluation": evaluate(results), "items": results}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
