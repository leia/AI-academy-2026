from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Tuple

import faiss
import numpy as np
from tqdm import tqdm

@dataclass
class DocumentChunk:
    text: str
    metadata: dict


def ingest_corpus(data_dir: Path, index_dir: Path) -> None:
    docs = load_documents(data_dir)
    chunks = chunk_documents(docs)
    # embedding function is injected to allow multiple providers
    raise RuntimeError("ingest_corpus now requires an embed_fn. Use ingest_corpus_with_embed.")
    persist_index(chunks, vectors, index_dir)


def ingest_corpus_with_embed(
    data_dir: Path, index_dir: Path, embed_fn: Callable[[List[str]], np.ndarray]
) -> Tuple[int, int]:
    docs = load_documents(data_dir)
    if not docs:
        raise ValueError(f"No ingestable files found under {data_dir}")

    chunks = chunk_documents(docs)
    if not chunks:
        raise ValueError(f"No text chunks produced from files under {data_dir}")

    vectors = embed_chunks(chunks, embed_fn)
    persist_index(chunks, vectors, index_dir)
    return len(docs), len(chunks)


def load_documents(data_dir: Path) -> List[DocumentChunk]:
    docs: List[DocumentChunk] = []
    for path in sorted(data_dir.glob("**/*")):
        if path.is_dir() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        meta = {
            "source": path.name,
            "path": str(path),
            "type": infer_type_from_name(path.name),
        }
        docs.append(DocumentChunk(text=text, metadata=meta))
    if not docs:
        raise ValueError(f"No ingestable files found under {data_dir}")
    return docs


def chunk_documents(docs: List[DocumentChunk], max_words: int = 220) -> List[DocumentChunk]:
    chunks: List[DocumentChunk] = []
    for doc in docs:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]
        for para in paragraphs:
            words = para.split()
            for i in range(0, len(words), max_words):
                slice_words = words[i : i + max_words]
                chunk_text = " ".join(slice_words)
                chunk_meta = {**doc.metadata, "chunk_start_word": i}
                chunks.append(DocumentChunk(text=chunk_text, metadata=chunk_meta))
    return chunks


def embed_chunks(chunks: List[DocumentChunk], embed_fn: Callable[[List[str]], np.ndarray]) -> np.ndarray:
    texts = [c.text for c in chunks]
    vectors = embed_fn(texts)
    return np.array(vectors, dtype="float32")


def persist_index(chunks: List[DocumentChunk], vectors: np.ndarray, index_dir: Path) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(index_dir / "index.faiss"))

    docstore = []
    for chunk in chunks:
        docstore.append({"text": chunk.text, "metadata": chunk.metadata})
    (index_dir / "docstore.json").write_text(json.dumps(docstore, indent=2), encoding="utf-8")


def infer_type_from_name(name: str) -> str:
    lowered = name.lower()
    if "requirement" in lowered:
        return "requirement"
    if "guideline" in lowered:
        return "guideline"
    if "pattern" in lowered:
        return "ambiguity_pattern"
    if "example" in lowered:
        return "example"
    return "unknown"
