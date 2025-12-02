"""
Disk-backed embedding cache to minimize repeated model calls.
"""

from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass
class EmbeddingCache:
    """Simple pickle-based cache keyed by hash of text or metadata."""

    path: Path
    _lock: Lock = Lock()

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self) -> dict[str, list[float]]:
        with self._lock:
            with self.path.open("rb") as handle:
                return pickle.load(handle)

    def _write(self, payload: dict[str, list[float]]) -> None:
        with self._lock:
            with self.path.open("wb") as handle:
                pickle.dump(payload, handle)

    def _hash(self, text: str, **metadata: Any) -> str:
        digest = hashlib.sha256()
        digest.update(text.encode("utf-8"))
        if metadata:
            digest.update(repr(sorted(metadata.items())).encode("utf-8"))
        return digest.hexdigest()

    def get(self, text: str, **metadata: Any) -> list[float] | None:
        payload = self._read()
        return payload.get(self._hash(text, **metadata))

    def set(self, text: str, vector: list[float], **metadata: Any) -> None:
        payload = self._read()
        payload[self._hash(text, **metadata)] = vector
        self._write(payload)

