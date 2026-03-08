"""
data_structures.py — Custom data structures: Queue and Graph.

All structures are hand-implemented to satisfy the module rubric
requirement for user-defined (non-built-in) data structures.
"""
from __future__ import annotations
import threading
from typing import Any, Optional
from core.models import PortResult


class _Node:
    """Internal linked-list node for CustomQueue."""

    __slots__ = ("value", "next_node")

    def __init__(self, value: Any) -> None:
        self.value = value
        self.next_node: Optional[_Node] = None


class CustomQueue:
    def __init__(self) -> None:
        self._head: Optional[_Node] = None
        self._tail: Optional[_Node] = None
        self._size: int = 0
        self._lock = threading.Lock()

    def enqueue(self, item: Any) -> None:
        """Add item to the tail of the queue. O(1)."""
        node = _Node(item)
        with self._lock:
            if self._tail is not None:
                self._tail.next_node = node
            self._tail = node
            if self._head is None:
                self._head = node
            self._size += 1

    def dequeue(self) -> Any:
        """Remove and return item from head. O(1). Raises IndexError if empty."""
        with self._lock:
            if self._head is None:
                raise IndexError("dequeue from empty CustomQueue")
            value = self._head.value
            self._head = self._head.next_node
            if self._head is None:
                self._tail = None
            self._size -= 1
            return value

    def peek(self) -> Any:
        """Return head item without removing. O(1)."""
        if self._head is None:
            raise IndexError("peek at empty CustomQueue")
        return self._head.value

    def is_empty(self) -> bool:
        """Return True if queue contains no elements."""
        return self._size == 0

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"CustomQueue(size={self._size})"


# ---------------------------------------------------------------------------

class NetworkGraph:

    def __init__(self) -> None:
        # dict[ip_str -> list[PortResult]]
        self._adjacency: dict[str, list[PortResult]] = {}

    def add_host(self, ip: str) -> None:
       
        if ip not in self._adjacency:
            self._adjacency[ip] = []

    def add_port(self, ip: str, port_result: PortResult) -> None:
       
        if ip not in self._adjacency:
            raise KeyError(f"Host '{ip}' not found in graph. Call add_host() first.")
        self._adjacency[ip].append(port_result)

    def get_hosts(self) -> list[str]:
        """Return list of all registered host IPs. O(n)."""
        return list(self._adjacency.keys())

    def get_ports(self, ip: str) -> list[PortResult]:
      
        if ip not in self._adjacency:
            raise KeyError(f"Host '{ip}' not in graph.")
        return self._adjacency[ip]

    def to_dict(self) -> dict:
        """Serialise the entire graph to a JSON-compatible dict."""
        return {
            ip: [pr.to_dict() for pr in ports]
            for ip, ports in self._adjacency.items()
        }

    def __repr__(self) -> str:
        return f"NetworkGraph(hosts={len(self._adjacency)})"
