# AI Delivery Risk & Requirement Analyzer

Lightweight agent that analyzes a requirement, retrieves context, flags ambiguities, generates clarification questions, scores delivery risk, and (optionally) reflects on its own output. Runs via CLI, API, or a small React UI; supports OpenAI, Claude, and Gemini for generation, and OpenAI or Gemini for embeddings.

📌 **Quickstart:** start with [docs/quickstart.md](docs/quickstart.md) for setup, ingest, run commands, ports, and troubleshooting.

---

## What It Does
- Retrieval-augmented analysis over a curated corpus (FAISS index)
- Structured JSON output (summary, ambiguities, questions, risk, confidence, reflection)
- Optional reflection pass to critique and adjust risk/confidence
- Decision trace logging for transparency
- Frontend demo to visualize results and traces

---

## Core Capabilities
- **Requirement analysis (RAG):** embed requirement, retrieve top-k context, ground prompts.
- **Ambiguity & questions:** heuristic patterns + LLM generate ambiguities and follow-ups.
- **Risk & confidence:** normalized scores (risk 0–1, confidence 0–1) with banding.
- **Reflection:** second pass critique; retries once if confidence is low; heuristics inject missing ambiguities if the model omits them.
- **Evaluation:** fixture-based sanity checks with summary hits.

---

## Architecture (condensed)
1) Ingest curated docs → chunk → embed → FAISS index  
2) Embed requirement → similarity search → top-k context  
3) LLM analysis + heuristics → structured JSON  
4) Optional reflection → adjusted confidence/risk, notes  
5) Trace + run log persisted (unless `--output`)

Diagram: see [docs/architecture.md](docs/architecture.md) (ASCII).

---

## Run It
### One-command dev (API + UI)
```powershell
.\scripts\dev.ps1   # API on 8787, Vite UI on 5173
```
Open http://localhost:5173.

### CLI
```bash
ai-analyze ingest data/curated --force
ai-analyze analyze --text "Improve dashboard UX..." --k 5 [--no-reflect] [--show-trace]
ai-analyze eval tests/fixtures/simple_eval.json
ai-analyze qa --question "What is the deadline?" --k 5
```

### API
```bash
uvicorn api:app --reload --port 8787
```
POST `http://localhost:8787/analyze`
```json
{ "text": "Improve dashboard UX...", "k": 5, "no_reflect": false, "show_trace": true }
```
POST `http://localhost:8787/qa`
```json
{ "question": "What is the deadline?", "k": 5 }
```

### Frontend (manual)
```bash
cd frontend && npm install && npm run dev   # default expects API at 8787
```

---

## Configuration
Set in `.env` (see `.env.example`):
- `LLM_PROVIDER`: `openai` | `claude` | `gemini`
- `EMBED_PROVIDER`: `openai` | `gemini`
- OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL` (e.g., `gpt-4o-mini`), `OPENAI_EMBED_MODEL` (e.g., `text-embedding-3-small`)
- Claude: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`
- Gemini: `GOOGLE_API_KEY`, `GEMINI_MODEL` (e.g., `gemini-1.5-pro-latest`), `GEMINI_EMBED_MODEL` (e.g., `models/gemini-embedding-001`)

Ports: API 8787, UI 5173.  
Rebuild index (`ai-analyze ingest ...`) when changing `EMBED_PROVIDER` or embed model.

---

## Output Contract
```json
{
  "summary": {"text": "string"},
  "ambiguities": [{"issue": "string", "impact": "string?", "severity": "low|medium|high?"}],
  "questions": ["string"],
  "risk": {"score": 0-1, "rationale": "string"},
  "confidence": 0-1,
  "reflection": "string"
}
```
Bands: risk low 0.0–0.2, medium 0.2–0.6, high 0.6–1.0; confidence low 0.0–0.3, moderate 0.3–0.7, high 0.7–1.0.

---

## Evaluation
Run: `ai-analyze eval tests/fixtures/simple_eval.json`  
Returns per-fixture hits for ambiguities/questions plus a summary.

---

## Troubleshooting
- **FAISS dimension error:** re-run `ai-analyze ingest ...` after changing embed provider/model.  
- **“Failed to fetch” (UI):** ensure API at `VITE_API_URL` (default 8787) is running.  
- **429/503 or “high demand”:** retries are built in; wait or switch model/provider.  
- **Missing keys:** check `.env` matches chosen providers.
- **QA empty/irrelevant answers:** verify index exists and includes PDFs; rerun ingest if you added/changed sources.

---

## Tech Stack
Python, FastAPI, Typer, FAISS, Pydantic, Rich, OpenAI/Anthropic/Gemini clients, React + Vite (frontend).

---

## Project Structure
```
src/
  main.py          # CLI entry
  api.py           # FastAPI app (/analyze)
  ai_analyzer/     # analysis pipeline, config, tools, prompts, reflection, eval
frontend/          # React UI (Vite)
data/curated/      # curated corpus
data/index/        # FAISS index (generated)
runs/              # run logs
docs/              # architecture, demo, quickstart
tests/             # fixtures and smoke placeholder
scripts/dev.ps1    # start API + frontend
```

---

## License
Educational project for AI Academy Capstone.
