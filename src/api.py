from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai_analyzer.analysis import ContextItem, run_analysis
from ai_analyzer.config import load_embed_config, load_llm_config
from ai_analyzer.embeddings import build_embed_fn
from ai_analyzer.qa import answer_question
from ai_analyzer.retrieval import embed_query, load_index, similarity_search


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Requirement text")
    k: int = Field(5, ge=1, le=20)
    no_reflect: bool = False
    show_trace: bool = False
    debug_raw: bool = False
    debug_reflect: bool = False


class QARequest(BaseModel):
    question: str = Field(..., description="Question to ask the indexed corpus")
    k: int = Field(5, ge=1, le=20)
    show_trace: bool = False


def create_app() -> FastAPI:
    app = FastAPI(title="AI Delivery Risk & Requirement Analyzer API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @lru_cache()
    def shared_llm_config():
        return load_llm_config()

    @lru_cache()
    def shared_embed_config():
        return load_embed_config()

    @lru_cache()
    def shared_index():
        from pathlib import Path
        return load_index(Path("data/index"))

    @lru_cache()
    def shared_embed_fn():
        return build_embed_fn(shared_embed_config())

    @app.post("/analyze")
    def analyze(req: AnalyzeRequest):
        try:
            index, docstore = shared_index()
            embed_fn = shared_embed_fn()
            llm_config = shared_llm_config()

            query_vec = embed_query(req.text, embed_fn)
            retrieved = similarity_search(query_vec, index, docstore, top_k=req.k)
            contexts = [ContextItem(text=r.text, metadata=r.metadata, score=r.score) for r in retrieved]

            trace: list = [{"step": "retrieval", "info": {"k": req.k, "retrieved": len(retrieved)}}] if req.show_trace else []
            report = run_analysis(
                req.text,
                contexts,
                llm_config,
                enable_reflection=not req.no_reflect,
                debug_raw=req.debug_raw,
                debug_reflect=req.debug_reflect,
                trace=trace if req.show_trace else None,
            )

            if req.show_trace:
                return {"report": report.model_dump(), "trace": trace}
            return report.model_dump()
        except HTTPException:
            raise
        except Exception as exc:
            # Surface the model/backend error so the frontend can display it
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/qa")
    def qa(req: QARequest):
        try:
            index, docstore = shared_index()
            embed_fn = shared_embed_fn()
            llm_config = shared_llm_config()

            query_vec = embed_query(req.question, embed_fn)
            retrieved = similarity_search(query_vec, index, docstore, top_k=req.k)
            contexts = [
                {"text": r.text, "metadata": r.metadata, "score": r.score}
                for r in retrieved
            ]
            trace = [{"step": "retrieval", "info": {"k": req.k, "retrieved": len(retrieved)}}] if req.show_trace else None

            answer = answer_question(req.question, contexts, llm_config)
            payload = {"question": req.question, "answer": answer, "retrieved": contexts}
            if trace:
                payload["trace"] = trace
            return payload
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app


app = create_app()
