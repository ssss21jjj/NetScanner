"""
algorithms.py — Custom sorting and fingerprinting algorithms.

merge_sort is implemented from scratch (no sorted() / list.sort() calls)
to satisfy the module rubric requirement for custom algorithm logic.
"""
from __future__ import annotations
from typing import Any, Callable, Optional


def merge_sort(
    arr: list[Any],
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> list[Any]:

    if len(arr) <= 1:
        return list(arr)

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key=key, reverse=reverse)
    right = merge_sort(arr[mid:], key=key, reverse=reverse)
    return _merge(left, right, key=key, reverse=reverse)


def _merge(
    left: list[Any],
    right: list[Any],
    key: Optional[Callable[[Any], Any]],
    reverse: bool,
) -> list[Any]:
    """Merge two sorted lists into one sorted list. O(n)."""
    result: list[Any] = []
    i = j = 0

    def _get(item: Any) -> Any:
        return key(item) if key else item

    while i < len(left) and j < len(right):
        left_val = _get(left[i])
        right_val = _get(right[j])
        condition = left_val > right_val if reverse else left_val <= right_val
        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ---------------------------------------------------------------------------
# Service fingerprinting heuristic — O(1) dict lookup

_SERVICE_MAP: dict[int, str] = {
    21: "FTP",    22: "SSH",    23: "Telnet",  25: "SMTP",
    53: "DNS",    80: "HTTP",   110: "POP3",   143: "IMAP",
    443: "HTTPS", 445: "SMB",   3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
}


def service_fingerprint(port: int) -> str:

    return _SERVICE_MAP.get(port, "Unknown")
