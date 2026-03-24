from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ai_analyzer.analysis import ContextItem, run_analysis
from ai_analyzer.config import load_embed_config, load_llm_config
from ai_analyzer.embeddings import build_embed_fn
from ai_analyzer.retrieval import embed_query, load_index, similarity_search


def run_fixture(fixture: Dict, index_dir: Path, k: int = 5) -> Dict:
    llm_config = load_llm_config()
    embed_config = load_embed_config()
    embed_fn = build_embed_fn(embed_config)

    index, docstore = load_index(index_dir)
    query_vec = embed_query(fixture["input"], embed_fn)
    retrieved = similarity_search(query_vec, index, docstore, top_k=k)
    contexts = [ContextItem(text=r.text, metadata=r.metadata, score=r.score) for r in retrieved]

    report = run_analysis(fixture["input"], contexts, llm_config, enable_reflection=False)

    return {
        "name": fixture["name"],
        "report": report.model_dump(),
        "checks": score_fixture(fixture, report),
    }


def score_fixture(fixture: Dict, report) -> Dict:
    ambiguities_text = " ".join([a.issue.lower() for a in report.ambiguities])
    questions_text = " ".join([q.lower() for q in report.questions])

    amb_hits = sum(1 for token in fixture.get("expect_ambiguities", []) if token.lower() in ambiguities_text)
    q_hits = sum(1 for token in fixture.get("expect_questions_contains", []) if token.lower() in questions_text)

    return {
        "ambiguity_hits": amb_hits,
        "question_hits": q_hits,
    }


def run_eval(fixtures_path: Path, index_dir: Path, k: int = 5) -> List[Dict]:
    fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))
    results = []
    for fx in fixtures:
        results.append(run_fixture(fx, index_dir, k=k))
    return results
