from __future__ import annotations

from collections.abc import Iterable

def join_sorted(values: Iterable[object]) -> str:
    return ", ".join(sorted(str(value) for value in values))
