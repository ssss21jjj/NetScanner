"""
scan_engine.py — Multithreaded TCP connect scan engine.

Uses CustomQueue for BFS-style target distribution across worker
threads. Results are placed in a thread-safe queue.Queue for
safe consumption by the Tkinter main thread via root.after().
"""
from __future__ import annotations
import socket
import threading
import queue
import time
from typing import Optional

from core.models import ScanJob, PortResult
from core.data_structures import CustomQueue, NetworkGraph
from core.algorithms import service_fingerprint


class ScanEngine:
    """
    Orchestrates a multithreaded TCP connect scan.

    The engine distributes (ip, port) pairs via a CustomQueue.
    Worker threads dequeue tasks, attempt TCP connection, and
    push PortResult objects to result_queue for UI consumption.

    Attributes:
        job         : ScanJob metadata.
        result_queue: Thread-safe queue for passing results to UI.
    """

    def __init__(self, job: ScanJob, result_queue: queue.Queue) -> None:
        self.job = job
        self.result_queue = result_queue
        self._stop_event = threading.Event()
        self._graph = NetworkGraph()
        self._task_queue: CustomQueue = CustomQueue()
        self._threads: list[threading.Thread] = []

    def _build_task_queue(self, targets: list[str]) -> None:
        """Enqueue all (ip, port) pairs. BFS ordering: each IP enqueued left-to-right."""
        for ip in targets:
            self._graph.add_host(ip)
            for port in range(self.job.port_start, self.job.port_end + 1):
                self._task_queue.enqueue((ip, port))

    def _tcp_connect(self, ip: str, port: int) -> Optional[PortResult]:
        start = time.monotonic()
        try:
            with socket.create_connection((ip, port), timeout=self.job.timeout):
                elapsed = (time.monotonic() - start) * 1000
                service = service_fingerprint(port)
                return PortResult(
                    port=port,
                    state="open",
                    service=service,
                    response_ms=round(elapsed, 2),
                )
        except (ConnectionRefusedError, OSError):
            return None

    def _worker(self) -> None:
        """Worker thread: dequeue tasks and perform TCP connects."""
        while not self._stop_event.is_set():
            try:
                ip, port = self._task_queue.dequeue()
            except IndexError:
                break   # queue exhausted

            result = self._tcp_connect(ip, port)
            if result:
                self._graph.add_port(ip, result)
                self.result_queue.put((ip, result))

        # Signal this worker is done
        self.result_queue.put(None)

    def start(self, targets: list[str]) -> None:
        """
        Launch worker threads to scan all targets.

        Args:
            targets: List of IPv4 address strings to scan.
        """
        self._build_task_queue(targets)
        for _ in range(self.job.threads):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        """Signal all workers to stop after their current task."""
        self._stop_event.set()

    def get_graph(self) -> NetworkGraph:
        """Return the NetworkGraph populated during scanning."""
        return self._graph
