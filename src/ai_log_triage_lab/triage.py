from __future__ import annotations

import json
from pathlib import Path


def classify(message: str, level: str) -> dict:
    text = message.lower()
    if "authentication" in text or "failure" in text:
        category = "access_or_integration"
        severity = "high"
        action = "review synthetic connector credentials and retry policy"
    elif "delayed" in text or level == "warning":
        category = "operational_delay"
        severity = "medium"
        action = "check recent synthetic events and queue status"
    else:
        category = "informational"
        severity = "low"
        action = "no immediate action"
    return {"category": category, "severity": severity, "explanation": f"Matched deterministic baseline for {category}.", "suggested_action": action}


def run(logs_path: Path, output_path: Path) -> dict:
    results = []
    for line in logs_path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        results.append({**item, "triage": classify(item["message"], item["level"])})
    summary = {"logs": len(results), "items": results}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
