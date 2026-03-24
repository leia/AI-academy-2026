# Demo Scenario

Input:
```
Improve dashboard UX and fix login issue before release.
```

Expected behavior:
- Retrieves top-k context from curated data.
- Flags ambiguities (vague UX, missing acceptance criteria, non-measurable goal).
- Generates clarification questions about specific UX issues, metrics, and login failure details.
- Produces a risk score in the medium-high band with low-moderate confidence if details are missing.

How to run:
```
ai-analyze ingest data/curated --force           # build index
ai-analyze analyze --text "Improve dashboard UX and fix login issue before release."
```

Flags:
- `--k` to adjust retrieved context size.
- `--no-reflect` to skip the reflection pass.
- `--debug-raw` / `--debug-reflect` to inspect model outputs.
