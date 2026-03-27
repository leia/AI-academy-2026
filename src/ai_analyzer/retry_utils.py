from __future__ import annotations

import random
import time
from typing import Optional, Callable, TypeVar

T = TypeVar("T")


def backoff_delay(attempt: int, base: float = 0.5, factor: float = 2.0, jitter: float = 0.2) -> float:
    return base * (factor ** attempt) * (1 + random.uniform(-jitter, jitter))


def with_retries(fn: Callable[[], T], attempts: int = 3, sleep_fn: Callable[[float], None] = time.sleep) -> T:
    last_exc: Optional[Exception] = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if attempt == attempts - 1:
                break
            sleep_fn(backoff_delay(attempt))
    if last_exc:
        raise last_exc
    raise RuntimeError("with_retries failed without exception")
