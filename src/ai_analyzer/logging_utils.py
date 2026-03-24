from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict


def ensure_runs_dir(base: Path = Path("runs")) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_run(payload: Dict[str, Any], runs_dir: Path = Path("runs")) -> Path:
    ensure_runs_dir(runs_dir)
    ts = time.strftime("%Y%m%d-%H%M%S")
    run_id = uuid.uuid4().hex[:8]
    path = runs_dir / f"run-{ts}-{run_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
