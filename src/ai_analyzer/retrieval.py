from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import faiss
import numpy as np
from numpy.linalg import norm


@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    score: float


def load_index(index_dir: Path):
    index_path = index_dir / "index.faiss"
    docstore_path = index_dir / "docstore.json"
    if not index_path.exists() or not docstore_path.exists():
        raise FileNotFoundError(f"Index not found in {index_dir}.")
    index = faiss.read_index(str(index_path))
    docstore = json.loads(docstore_path.read_text(encoding="utf-8"))
    return index, docstore


def similarity_search(query_embedding: np.ndarray, index, docstore, top_k: int = 5) -> List[RetrievedChunk]:
    # Guard: dimension mismatch (e.g., index built with a different embed model)
    if query_embedding.shape[1] != index.d:
        raise ValueError(
            f"Index dimension ({index.d}) does not match query embedding ({query_embedding.shape[1]}). "
            "Re-run ingestion with the current embed model/provider."
        )
    # Normalize for cosine/IP retrieval if index expects it
    if not np.allclose(norm(query_embedding), 0):
        query_embedding = query_embedding / norm(query_embedding, axis=1, keepdims=True)
    scores, ids = index.search(query_embedding, top_k)
    results: List[RetrievedChunk] = []
    for score, idx in zip(scores[0], ids[0]):
        doc = docstore[int(idx)]
        results.append(RetrievedChunk(text=doc["text"], metadata=doc["metadata"], score=float(score)))
    return results


def embed_query(text: str, embed_fn) -> np.ndarray:
    """Embed a single query using the provided embedding function."""
    return embed_fn([text])
