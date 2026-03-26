# Quickstart

Follow these steps to run the analyzer locally with UI, API, and CLI.

## 1) Prerequisites
- Python 3.10+
- Node 18+ (for frontend)
- API keys for your chosen providers (set in `.env`)

## 2) Environment setup
```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e .
```
Copy `.env.example` to `.env` and set:
- `LLM_PROVIDER` (`openai` | `claude` | `gemini`)
- `EMBED_PROVIDER` (`openai` | `gemini`)
- Provider keys/models (OpenAI: `OPENAI_API_KEY`, Claude: `ANTHROPIC_API_KEY`, Gemini: `GOOGLE_API_KEY`, etc.)

## 3) Build the index
```bash
ai-analyze ingest data/curated --force
```
(Re-run if you change `EMBED_PROVIDER` or the embed model.)

## 4) Run API + Frontend (one command)
```powershell
.\scripts\dev.ps1    # API on 8787, frontend on 5173
```
Or manually:
```bash
uvicorn api:app --reload --port 8787
cd frontend && npm install && npm run dev
```
Open http://localhost:5173 (frontend calls API at http://localhost:8787 by default).

## 5) Use the CLI
- Analyze: `ai-analyze analyze --text "..." --k 5 [--no-reflect] [--show-trace]`
- Eval fixtures: `ai-analyze eval tests/fixtures/simple_eval.json`

## 6) Use the API directly
POST `http://localhost:8787/analyze`
```json
{
  "text": "Improve dashboard UX and fix login issue before release.",
  "k": 5,
  "no_reflect": false,
  "show_trace": true
}
```

## 7) Ports
- API: 8787 (change with `--port` and set `VITE_API_URL` for frontend)
- Frontend: 5173 (Vite dev server)

## 8) Troubleshooting
- **FAISS dimension error**: rerun `ai-analyze ingest ...` after changing embed provider/model.
- **“Model high demand” / 429 / 503**: retry; switch provider/model if persistent (retries are built in).
- **“Failed to fetch” in UI**: ensure API is running and `VITE_API_URL` matches; check console error detail.
- **Empty ambiguities on vague input**: heuristics may inject ambiguities/questions and adjust risk/confidence.

## 9) Logs & Debug
- Run logs in `runs/` (unless you use `--output`).
- `--show-trace` adds step-by-step trace.
- `--debug-raw`, `--debug-reflect` print model raw outputs.

## 10) Bands
- Risk: low 0.0–0.2, medium 0.2–0.6, high 0.6–1.0
- Confidence: low 0.0–0.3, moderate 0.3–0.7, high 0.7–1.0
