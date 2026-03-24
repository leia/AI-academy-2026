## Architecture (ASCII view)

```
  [ CLI / API ]
        |
        v
  Embed requirement
    (OpenAI / Gemini)
        |
        v
   FAISS search
        |
        v
  Top-k context chunks
        |
        v
  LLM analysis prompt
        |
        v
  Helper heuristics
        |
        v
  Reflection (optional)
        |
        v
  ClarificationReport JSON
        |
        v
  Run log (runs/)
```
