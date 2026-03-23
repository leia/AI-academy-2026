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
* **LLM:** OpenAI API
* **Retrieval:** Embeddings + vector store (or lightweight retrieval)
* **Architecture:** Modular agent pipeline with tool orchestration

---

## 📊 Evaluation Approach

The system evaluates its outputs using:

* Completeness of clarification
* Relevance of generated questions
* Consistency with retrieved context
* Self-reflection scoring mechanism

---

## 🚀 Conclusion

This project demonstrates how agentic AI systems can be applied to real-world delivery challenges by combining structured reasoning, contextual knowledge retrieval, and iterative self-evaluation.

Rather than replacing human decision-making, the agent acts as a support layer that enhances requirement clarity, reduces ambiguity, and improves alignment across teams.
