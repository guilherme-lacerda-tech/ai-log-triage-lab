from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pathlib import Path

from ai_log_triage_lab.triage import run


ROOT = Path(__file__).resolve().parents[1]
summary = run(ROOT / "data" / "sample" / "synthetic_logs.jsonl", ROOT / "reports" / "generated" / "triage.json")
print(f"Logs triaged: {summary['logs']}")
print(f"First category: {summary['items'][0]['triage']['category']}")
