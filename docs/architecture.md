    # Architecture

    ## Design Goal

    Build a safe AI-ready log triage lab using synthetic logs and structured output.

    ## Current Boundaries

    - Standard library first.
    - Synthetic input only.
    - Generated output ignored by Git.
    - No real systems, endpoints or credentials.

    ## Decisions

    - Start with deterministic baseline.
- Add LLM only as optional product functionality.
- Never use real logs.

    ## Future Layers

    ```mermaid
    flowchart TB
        A["Mock inputs"] --> B["Collector / Loader"]
        B --> C["Domain validation"]
        C --> D["Rules / Processing"]
        D --> E["Persistence"]
        E --> F["API / Reporting"]
        F --> G["Automation workflows"]
    ```
