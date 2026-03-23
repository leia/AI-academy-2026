# 🚀 Implementation Progress — AI Delivery Risk & Requirement Analyzer

Living checklist tracking the build-out of the agentic requirement analyzer. Use this to align scope, surface blockers early, and keep outputs predictable.

Status legend: `[ ]` not started, `[~]` in progress, `[x]` done.

## 📐 Scope & Output Schema
- [x] Finalize pydantic models for `RequirementSummary`, `Ambiguity`, `RiskAssessment`, `ClarificationReport` (fields: summary, ambiguities, questions, risk_score 0-1, reflection, confidence).
- [x] Document the JSON contract in README and CLI help.
- [x] Define risk/confidence scales and wording bands for consistent messaging.

## 📚 Curated Knowledge Base
- [ ] Assemble curated dataset: sample requirements, ambiguity patterns, requirement-writing guidelines, clarified exemplars.
- [ ] Normalize format/metadata (source, type, tags) and store under `data/curated/`.
- [ ] Capture provenance/version notes for future refreshes.

## 🔎 Ingestion & Retrieval
- [ ] `ingest` command: load curated docs, light chunking, embed, persist index (`data/index/`) with FAISS/Chroma.
- [ ] Retrieval service: top-k search with source tags and deterministic embedding cache to avoid recompute.
- [ ] Idempotent re-runs and graceful missing-data warnings.

## 🧠 Core Analysis Pipeline
- [ ] Orchestrated flow: retrieve context -> LLM reasoning -> helper tools -> merge into structured JSON.
- [ ] Helper tools: ambiguity detector (pattern/regex), risk scorer (weighted heuristics), follow-up question generator (templates + LLM fill).
- [ ] Lightweight run logs (inputs/outputs) stored under `runs/` for traceability.

## 🔁 Self-Reflection Pass
- [ ] Secondary LLM critique to flag missing info/over-assumptions, adjust confidence, optionally revise the report.
- [ ] Configurable toggle and cost guardrails.
- [ ] Reflection notes appended to final output.

## 🛠️ CLI & Evaluation
- [ ] CLI commands: `ingest`, `analyze --text|--file`, `eval` (fixture-driven smoke checks).
- [ ] Evaluation harness: 3-5 fixtures scored against expected ambiguities/questions; printed scorecard.
- [ ] `.env` validation with clear failure messages (OpenAI key, model name).

## 📝 Documentation & Quality
- [ ] README update: workflow, data layout, CLI examples, output schema.
- [ ] Architecture diagram (Mermaid/ASCII) in `docs/`.
- [ ] Demo scenario script with expected sample output.
- [ ] Smoke tests for ingest/analyze happy paths; note deferred full test suite.

## 🎯 Immediate Focus
- [ ] Scaffold project structure (`src/`, `cli.py`, `data/curated/`, `.env.example`, `pyproject.toml`).
- [ ] Choose and pin dependency set (OpenAI, pydantic, python-dotenv, typer/rich, FAISS/Chroma).
- [ ] Draft curated data stubs to unblock ingestion pipeline development.
