# 🚀 AI Delivery Risk & Requirement Analyzer
### A focused agentic system for de-risking software requirements

An intelligent AI system built as part of the **Ciklum AI Academy** capstone project.

This project applies **agentic patterns, Retrieval-Augmented Generation (RAG), structured reasoning, and self-reflection** to a real-world problem:

> unclear requirements that lead to costly delivery issues.

Instead of generating more content, this system **questions, structures, and evaluates requirements before they become problems**.

---

## 🌟 Core Capabilities

This system focuses on practical, delivery-oriented capabilities:

### 📊 1. Requirement Analysis (RAG-grounded)
- Embeds input requirement and retrieves top-k relevant context
- Grounds reasoning in curated domain examples
- Produces structured outputs (ambiguities, questions, risks)

**Example:**  
*"Make the dashboard more intuitive and fix login issues"*

---

### ❓ 2. Ambiguity Detection & Clarification
- Detects vague or incomplete statements using:
  - heuristic patterns
  - LLM reasoning
- Generates actionable clarification questions

**Example Output:**
- “more intuitive” is not measurable  
- Missing acceptance criteria  

---

### ⚠️ 3. Risk & Confidence Scoring
- Normalized scoring (0–1)
- Risk banding (low / medium / high)
- Short rationale explaining the score

---

### 🔁 4. Self-Reflection & Refinement
- Second-pass critique of initial output
- Identifies over-assumptions
- Adjusts confidence and risk
- Optional retry if confidence is low

---

### 📚 5. QA over Indexed Documents
- Ask questions over indexed knowledge base
- Context-only answers (no hallucinated content)
- Supports TXT / MD / PDF sources

**Example:**  
*"What is the deadline for this feature?"*

---

### 📜 6. Tracing & Logging
- Optional decision trace for each run
- Logs stored for reproducibility
- Enables inspection of agent behavior

---

## 🏗️ Architecture

The system follows a structured agentic pipeline:

```
User Input
        ↓
📥 Retrieval (RAG)
        ↓
🧠 Analysis (LLM + heuristics)
        ↓
🔧 Tool Application
        ↓
🔍 Reflection
        ↓
📊 Scoring (risk & confidence)
        ↓
📦 Structured Output
        ↓
🤖 Persistence
```

---

## 🧠 Agentic Features

### 🧠 Reasoning & Decomposition
- Breaks requirements into components:
  - ambiguities
  - assumptions
  - risks
  - questions

### 🔧 Tool-based Processing
- Uses lightweight tools to guide analysis
- Combines deterministic heuristics with LLM reasoning:
  - **Deterministic layer**: regex/pattern ambiguity detector, heuristic risk weights, templated follow‑ups.
  - **LLM layer**: fills templated questions, rewrites/normalizes risks, refines summaries, and runs the reflection critique.
  - **Prompt grounding**: retrieved chunks + heuristic hints are fed into the LLM to keep generations anchored.

### 🔍 Self-Reflection Loop
- Evaluates output quality - runs a second pass that critiques the first report against the same context
- Adjusts results based on critique - Flags over‑assumptions or missing acceptance criteria; can inject a confidence downgrade
- Reduces hallucination and overconfidence - Optionally rewrites risk/confidence bands; if confidence is very low, a single retry is allowed
- It shares the same retrieved context (no new retrieval)

### 📊 Evaluation Metrics

The system evaluates outputs based on:

- **Ambiguity Detection** 
  - how many unclear areas were identified
  - fixture eval counts expected ambiguity strings
- **Question Coverage** 
  - relevance of clarification questions
  - counts expected clarification questions per fixture
- **Completeness** – coverage of requirement dimensions  
- **Confidence Calibration** 
  - alignment of confidence with output quality  
  - flags mismatches between confidence band and detected ambiguity/risk density
- **QA faithfulness**: (for QA mode) answer must be supported by retrieved chunks; otherwise marked low

---

## 🧰 Built-in Tools

- **retrieval** – FAISS-based vector search  
- **ambiguity detector** – regex/pattern heuristics  
- **risk scorer** – weighted scoring logic  
- **follow-up generator** – structured question generation  
- **QA answerer** – concise context-based answers  
- **doc lister** – inspect indexed documents  

---

## 🖥️ Frontend Demo

A lightweight **React + Vite UI** is included:

- Paste a requirement or ask a question
- Run analysis or QA
- View:
  - ambiguities
  - questions
  - risk
  - confidence
  - reflection output
  - decision trace

The UI is intentionally simple to highlight the system’s reasoning.

---

## 🚀 Quick Start
### CLI
```bash
ai-analyze ingest data/curated --force
ai-analyze analyze --text "Improve dashboard UX..." --k 5 [--no-reflect] [--show-trace]
ai-analyze qa --question "What is the deadline?" --k 5
ai-analyze list-docs
ai-analyze eval tests/fixtures/simple_eval.json
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

### Frontend
```bash
cd frontend && npm install && npm run dev   # expects API at 8787 (set VITE_API_URL to change)
```
Open http://localhost:5173.

---

### 🗂 Data & Index
- Place sources in `data/curated/`.  
- Optional: put QA‑only sources in `data/curated/qa/` — QA will prefer these but still fall back to requirement‑type chunks elsewhere.  
- Rebuild index after adding/moving files or changing embed provider/model: `ai-analyze ingest data/curated --force`.  
- Generated index lives in `data/index/` (FAISS + docstore JSON).

---

### 📤 Output Contract
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

### 🔧 Configuration (env)
- `LLM_PROVIDER`: `openai` | `claude` | `gemini`  
- `EMBED_PROVIDER`: `openai` | `gemini`  
- OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL` (e.g., `gpt-4o-mini`), `OPENAI_EMBED_MODEL` (e.g., `text-embedding-3-small`)  
- Claude: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`  
- Gemini: `GOOGLE_API_KEY`, `GEMINI_MODEL` (e.g., `gemini-1.5-pro-latest`), `GEMINI_EMBED_MODEL` (e.g., `models/gemini-embedding-001`)  
Ports: API 8787, UI 5173.

---

### 🧪 Evaluation
`ai-analyze eval tests/fixtures/simple_eval.json` — lightweight checks for expected ambiguities/questions and summary hits; prints a scorecard.

---

## 🛠 Tech Stack
  - Language: `Python 3.11`
  - LLMs: `OpenAI` / `Anthropic Claude` / `Google Gemini` (switchable via .env)
  - Embeddings: OpenAI `text-embedding-3-small` or Gemini `models/gemini-embedding-001`
  - Vector DB: `FAISS` (persistent)
  - APIs/UI: `FastAPI` backend (8787) + `React/Vite` frontend (5173); Typer CLI
  - Config: `python-dotenv`; `Pydantic` models; `Rich` for CLI output; runs stored to runs/

---

## 📁 Project Structure
```
src/
  main.py          # CLI entry
  api.py           # FastAPI app (/analyze, /qa)
  ai_analyzer/     # pipeline, heuristics, reflection, eval, retrieval
frontend/          # React UI (Vite)
data/curated/      # curated corpus (txt/md/pdf)
  qa/              # optional QA-focused docs
data/index/        # FAISS index (generated)
runs/              # run logs
docs/              # architecture, demo, quickstart
tests/             # fixtures and smoke placeholder
scripts/dev.ps1    # start API + frontend together
```

---

## 🎯 Use Cases

### Delivery Risk Reduction
- Identify unclear requirements early
- Prevent scope misunderstandings

### Engineering Support
- Generate clarification questions
- Improve requirement quality before implementation

### Knowledge Navigation
- Query project documentation
- Extract key information quickly

---

## 📈 Future Enhancements

- [ ] Multi-turn memory
- [ ] Improved evaluation metrics
- [ ] More advanced planning loop
- [ ] Integration with ticketing systems (Jira, Azure DevOps)
- [ ] Larger domain datasets
- [ ] Automated feedback learning

---

## 🤝 Contributing

- This is an educational project, contributions are welcome!
- Fork the repo and create a new branch for your feature/fix
- Ensure code is well-documented and tested
- Submit a pull request with a clear description of changes

## 🛠 Troubleshooting

- `“Index not found” / FAISS errors`: Re-run ai-analyze ingest data/curated --force after adding/moving files or changing EMBED_PROVIDER/embed model.
- `Dimension mismatch`: You changed embed model/provider without reingesting. Rebuild the index.
- `“Failed to fetch” in UI`: Ensure API is running on 8787 (or update VITE_API_URL), and the frontend points to it; check CORS/console logs.
- `429/503 or “model high demand`”: Retry; switch provider/model; ensure correct API key/region; backoff is limited.
- `Missing API keys/config`: Verify .env matches selected LLM_PROVIDER/EMBED_PROVIDER; restart after edits.
- `QA returns empty/irrelevant answers`: Make sure your QA docs are ingested (try ai-analyze list-docs); place QA-focused files under data/curated/qa/; reingest.
- `Reflection/parse issues`: Use --debug-raw / --debug-reflect to inspect raw model output; temporarily disable with --no-reflect if blocking.
- `CORS/port conflicts`: Change API port with uvicorn ... --port XXXX and set VITE_API_URL accordingly; ensure no other service is on the chosen port.

## 📝 License

Educational project for AI Academy 2025/2026
