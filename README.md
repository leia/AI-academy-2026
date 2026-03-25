# AI Delivery Risk & Requirement Analyzer

## 📘 Overview

The **AI Delivery Risk & Requirement Analyzer** is a small prototype that explores how AI can help improve the quality and clarity of incoming software requirements.

Ambiguous or incomplete requirements are a common source of delivery risk. They often lead to misunderstandings, rework, and delays. This project focuses on analyzing requirement inputs, highlighting potential issues, and generating structured clarification outputs that can be used by engineers or product stakeholders.

The system combines retrieval (RAG), structured prompting, and a simple reflection step to produce more consistent and context-aware results.

---

## 🎯 Objective

The goal of this project is to build a lightweight system that can:

* Analyze incoming requirements (tickets, notes, summaries)
* Detect ambiguity and missing information
* Generate useful follow-up questions
* Provide a rough delivery risk estimate
* Review its own output and highlight potential issues

The focus is on clarity and practicality rather than completeness.

---

## 🧠 Key Features

### 1. Requirement Analysis

The system processes unstructured input and breaks it down into:

* Feature requests
* Bug fixes
* UX improvements
* Implicit assumptions

### 2. Ambiguity Detection

The system looks for vague or underspecified language such as:

* Non-measurable goals (e.g. “improve usability”)
* Missing constraints or acceptance criteria
* Unclear scope or dependencies

### 3. Context-Aware Reasoning (RAG)

The system uses a small local knowledge base with examples and guidelines, including:

* Sample requirements
* Best practice templates
* Common ambiguity patterns

Relevant context is retrieved and included in the prompt so the model has something concrete to work with.

### 4. Tool-Based Workflow

Instead of a single large prompt, the system splits the work into smaller steps (e.g. ambiguity detection, question generation, risk estimation).

This makes the output easier to control and reason about.

### 5. Delivery Risk Assessment

The system evaluates each requirement and assigns a rough risk score based on:

* Ambiguity level
* Missing information
* Implementation uncertainty

### 6. Self-Reflection & Evaluation

After generating the initial result, the system runs a second pass where the model reviews its own output.

It checks for missing information, over-assumptions, and overall completeness, and assigns a simple confidence score.

---

## ⚙️ System Workflow

1. **Input Processing**
   The user provides a requirement (e.g. ticket, message, or summary).

2. **Context Retrieval (RAG)**
   Relevant examples and guidelines are retrieved from the knowledge base.

3. **Reasoning & Decomposition**
   The system analyzes the requirement and identifies key components.

4. **Step Execution**
   The system runs several steps in sequence to:

   * Detect ambiguities
   * Generate clarification questions
   * Assess delivery risk

5. **Self-Reflection**
   The system reviews its own output and improves it if needed.

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

* Risk assessment (rough estimate):

  * Ambiguity: High
  * Implementation risk: Medium
  * Confidence: 7/10

---

## 🧰 Technology Stack

* **Language:** Python
* **Embeddings:** `openai` or `gemini` (configurable, independent of LLM choice)
* **LLM:** OpenAI API
* **Retrieval:** lightweight local vector store (FAISS)
* **Architecture:** modular pipeline with simple step orchestration

---

## 📊 Evaluation Approach

The system includes a simple evaluation step based on predefined test cases.

It checks things like:

* Whether key ambiguities were detected
* Whether useful follow-up questions were generated
* Overall completeness of the output

This is not meant to be a rigorous benchmark, but rather a sanity check for the system’s behavior.

---

## ⌨️ CLI Usage

* Build index: `ai-analyze ingest data/curated --force`
* Analyze: `ai-analyze analyze --text "..." --k 5 [--no-reflect] [--debug-raw] [--debug-reflect]`
* Eval fixtures: `ai-analyze eval tests/fixtures/simple_eval.json`

Flags:
* `--k` control top-k context
* `--no-reflect` skip reflection pass
* `--debug-raw` print analysis model output
* `--debug-reflect` print reflection model output

---

## 🗂️ Data Layout

* Curated corpus: `data/curated/` (with inline metadata headers)
* Index: `data/index/`
* Run logs: `runs/`

---

## 📐 Structured Output Contract

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

## 🧭 Workflow (condensed)

1) Ingest curated docs -> embed -> FAISS index  
2) Embed requirement -> similarity search -> top-k context  
3) LLM analysis + heuristics -> structured JSON  
4) Optional reflection pass -> adjusted confidence/risk, notes  
5) Log run to `runs/` unless `--output` is used

---
## 🚀 Conclusion

This project explores how a relatively simple AI pipeline can help surface issues in requirements and support better communication between stakeholders and engineering teams.

The goal is not to replace human judgment, but to provide a structured starting point that reduces ambiguity and highlights potential risks early.
