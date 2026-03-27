from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict


def load_docstore(index_dir: Path) -> List[Dict]:
    docstore_path = index_dir / "docstore.json"
    if not docstore_path.exists():
        raise FileNotFoundError(f"Docstore not found in {index_dir}")
    return json.loads(docstore_path.read_text(encoding="utf-8"))


def list_documents(index_dir: Path) -> List[Dict]:
    docs = load_docstore(index_dir)
    seen = {}
    for doc in docs:
        meta = doc.get("metadata", {})
        key = meta.get("path") or meta.get("source")
        if key and key not in seen:
            seen[key] = {
                "source": meta.get("source"),
                "path": meta.get("path"),
                "type": meta.get("type", "unknown"),
            }
    return list(seen.values())
