# Architecture

## Design Goal

Build an AI-ready log triage lab by first creating a deterministic, explainable baseline on synthetic logs.

## Flow

```mermaid
flowchart LR
    Logs["Synthetic JSONL logs"] --> Parser["LogEntry loader"]
    Parser --> Baseline["Rule baseline"]
    Baseline --> Result["TriageResult"]
    Result --> Eval["Labeled dataset evaluation"]
```

## Future LLM Comparison

The deterministic baseline is the first comparison target. A future LLM or Ollama implementation should be evaluated against the same labeled dataset instead of replacing the baseline without evidence.
