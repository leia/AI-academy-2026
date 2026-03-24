# AI Delivery Risk & Requirement Analyzer

## 📘 Overview

The **AI Delivery Risk & Requirement Analyzer** is an agentic AI system designed to improve the quality and clarity of incoming software requirements in enterprise environments.

Ambiguous, incomplete, or inconsistent requirements are a major source of delivery risk, often leading to misalignment, rework, and delayed releases. This project demonstrates how an AI agent can analyze requirement inputs, identify risks, and generate structured clarification outputs to support better decision-making and communication between stakeholders and engineering teams.

The system combines retrieval-augmented generation (RAG), multi-step reasoning, tool-based execution, and self-reflection to produce reliable, context-aware results.

---

## 🎯 Objective

The goal of this project is to design and implement a lightweight agentic AI system that:

* Analyzes incoming requirements from multiple sources (tickets, notes, summaries)
* Detects ambiguity, missing information, and potential risks
* Generates structured clarification artifacts and follow-up questions
* Evaluates its own outputs and iteratively improves response quality

---

## 🧠 Key Features

### 1. Requirement Analysis

The agent processes unstructured input and decomposes it into:

* Feature requests
* Bug fixes
* UX improvements
* Implicit assumptions

### 2. Ambiguity Detection

The system identifies vague or under-specified language such as:

* Non-measurable goals (e.g., “improve usability”)
* Missing constraints or acceptance criteria
* Undefined scope or dependencies

### 3. Context-Aware Reasoning (RAG)

The agent retrieves relevant examples and guidelines from a curated knowledge base, including:

* Sample requirements
* Best practice templates
* Common ambiguity patterns

This context is used to ground the agent’s reasoning and improve output relevance.

### 4. Tool-Based Agent Workflow

The system operates as a multi-step agent that orchestrates specialized tools, such as:

* Context retrieval
* Ambiguity extraction
* Question generation
* Risk assessment

### 5. Delivery Risk Assessment

The agent evaluates each requirement and assigns a risk score based on:

* Ambiguity level
* Missing information
* Potential implementation uncertainty

### 6. Self-Reflection & Evaluation

After generating results, the agent performs a self-evaluation step:

* Reviews completeness and correctness
* Identifies over-assumptions
* Assigns a confidence score
* Optionally refines its output

---

## ⚙️ System Workflow

1. **Input Processing**
   The user provides a requirement (e.g., ticket, message, or summary).

2. **Context Retrieval (RAG)**
   Relevant examples and guidelines are retrieved from the knowledge base.

3. **Reasoning & Decomposition**
   The agent analyzes the requirement and identifies key components.

4. **Tool Execution**
   The agent invokes specialized tools to:

   * Detect ambiguities
   * Generate clarification questions
   * Assess delivery risk

5. **Self-Reflection**
   The agent evaluates its own output and improves it if necessary.

6. **Final Output**
   The system produces a structured clarification report.

---

## 📦 Example Output

**Input:**

> “Improve dashboard UX and fix login issue before release.”

**Output:**

* Identified areas:

  * UX improvement (undefined scope)
  * Authentication bug (missing error details)

* Detected ambiguities:

  * “Improve UX” is not measurable
  * No definition of expected behavior or success criteria

* Suggested clarification questions:

  * What specific usability issues should be addressed?
  * Are there existing UX metrics or feedback sources?
  * What is the exact login failure scenario?

* Risk assessment:

  * Ambiguity: High
  * Implementation risk: Medium
  * Confidence: 7/10

---

## 🧰 Technology Stack

* **Language:** Python
* **LLM:** `openai` (default), `claude`, or `gemini`.
* **Embeddings:** `openai` or `gemini` (configurable, independent of LLM choice)
* **Retrieval:** Embeddings + FAISS
* **Architecture:** Modular agent pipeline with tool orchestration

---

The system evaluates its outputs using:

* Completeness of clarification
* Relevance of generated questions
* Consistency with retrieved context
* Self-reflection scoring mechanism
## Structured Output Contract
The analyzer returns a single JSON object:
- `summary` — one or two sentences restating the requirement.
- `ambiguities` — array of `{ issue, impact?, severity? }`.
- `questions` — list of clarification questions.
- `risk` — `{ score, rationale? }`, where `score` is 0–1 (higher = greater delivery risk).
- `confidence` — number 0–1 (self-reported confidence in the report).
- `reflection` — optional self-critique or notes on assumptions.

### Risk & Confidence Bands
- Risk: 0.0–0.2 low; 0.2–0.6 medium; 0.6–1.0 high.
- Confidence: 0.0–0.3 low; 0.3–0.7 moderate; 0.7–1.0 high. If confidence < 0.5, reflection should explain why.

### Configuration
  - `LLM_PROVIDER`: `openai` | `claude` | `gemini`
  - `EMBED_PROVIDER`: `openai` | `gemini`
  - Models and keys are set in `.env` (see `.env.example`):
    - OpenAI: `OPENAI_MODEL`, `OPENAI_EMBED_MODEL`, `OPENAI_API_KEY`
    - Claude: `ANTHROPIC_MODEL`, `ANTHROPIC_API_KEY`
  - Gemini: `GEMINI_MODEL`, `GEMINI_EMBED_MODEL` (e.g., `text-embedding-004`), `GOOGLE_API_KEY`
  - The LLM provider (generation) is independent of the embedding provider (retrieval). Choose any combination without code changes.

## Conclusion
This system aims to support delivery planning by combining structured reasoning, contextual retrieval, and iterative self-evaluation—augmenting, not replacing, human decision-making.
