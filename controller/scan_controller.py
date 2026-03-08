"""
scan_controller.py — Orchestrates scan lifecycle between UI and engine.
"""
from __future__ import annotations
import queue
import threading
from tkinter import filedialog
from typing import TYPE_CHECKING

from controller.input_validator import expand_targets, validate_port_range, validate_timeout
from core.models import ScanJob
from core.scan_engine import ScanEngine
from core.algorithms import merge_sort
from storage.sqlite_repo import SQLiteRepository
from storage.file_repo import FileRepository

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ScanController:
    """Connects UI events to the scan engine and storage layer."""

    def __init__(self, view: "MainWindow") -> None:
        self._view = view
        self._engine: ScanEngine | None = None
        self._result_queue: queue.Queue = queue.Queue()
        self._db = SQLiteRepository()
        self._file_repo = FileRepository()
        self._active_job: ScanJob | None = None
        self._workers_done = 0
        self._total_workers = 0

    # ------------------------------------------------------------------
    # Scan lifecycle
    # ------------------------------------------------------------------

    def start_scan(self) -> None:
        """Validate inputs, build engine, launch workers, start polling."""
        params = self._view.scan_form.get_params()

        # Validate
        try:
            validate_port_range(params["port_start"], params["port_end"])
            validate_timeout(params["timeout"])
            targets = expand_targets(params["target"])
        except ValueError as e:
            self._view.show_error("Invalid Input", str(e))
            return

        # Clear previous results
        self._view.results_frame.clear()
        self._workers_done = 0
        self._total_workers = params["threads"]
        self._result_queue = queue.Queue()

        # Build job + engine
        self._active_job = ScanJob(
            target=params["target"],
            port_start=params["port_start"],
            port_end=params["port_end"],
            timeout=params["timeout"],
            threads=params["threads"],
        )
        self._engine = ScanEngine(self._active_job, self._result_queue)
        self._engine.start(targets)

        # Update UI state
        self._view.scan_form.set_scanning(True)
        self._view.status_bar.set_status(
            f"Scanning {params['target']} | ports {params['port_start']}–{params['port_end']}..."
        )
        self._view.status_bar.start_progress()

        # Start polling loop
        self._view.root.after(100, self._poll_results)

    def stop_scan(self) -> None:
        """Signal engine to stop."""
        if self._engine:
            self._engine.stop()
        self._finish_scan()

    def _poll_results(self) -> None:
        """
        Called every 100ms by Tkinter event loop.
        Drains result_queue and updates Treeview safely from main thread.
        """
        try:
            while True:
                item = self._result_queue.get_nowait()
                if item is None:
                    # One worker finished
                    self._workers_done += 1
                    if self._workers_done >= self._total_workers:
                        self._finish_scan()
                        return
                else:
                    ip, port_result = item
                    self._view.results_frame.add_row(
                        ip,
                        port_result.port,
                        port_result.state,
                        port_result.service,
                        port_result.response_ms,
                    )
        except queue.Empty:
            pass

        # Reschedule if scan still running
        if self._engine and not self._engine._stop_event.is_set():
            self._view.root.after(100, self._poll_results)

    def _finish_scan(self) -> None:
        """Clean up UI after scan completes or is stopped."""
        self._view.scan_form.set_scanning(False)
        self._view.status_bar.stop_progress()
        self._view.status_bar.set_status("Scan complete. Ready.")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def on_save(self) -> None:
        """Save current scan results to SQLite database."""
        if not self._engine or not self._active_job:
            self._view.show_error("No Scan", "Run a scan first before saving.")
            return
        graph = self._engine.get_graph()
        self._db.save_scan(self._active_job, graph)
        self._view.show_info("Saved", f"Scan saved to database.\nJob ID: {self._active_job.job_id}")

    def on_export(self) -> None:
        """Export current scan results to JSON file."""
        if not self._engine or not self._active_job:
            self._view.show_error("No Scan", "Run a scan first before exporting.")
            return
        graph = self._engine.get_graph()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")],
            initialfile=f"scan_{self._active_job.job_id}.json",
        )
        if path:
            if path.endswith(".csv"):
                self._file_repo.export_csv(graph, path.split("/")[-1])
            else:
                self._file_repo.export_json(graph, path.split("/")[-1])
            self._view.show_info("Exported", f"Results saved to:\n{path}")

    def on_load(self) -> None:
        """Load previous scans from database into Treeview."""
        scans = self._db.list_scans()
        if not scans:
            self._view.show_info("No Scans", "No saved scans found in database.")
            return
        # Load the most recent scan
        latest = scans[0]
        graph = self._db.load_scan(latest["job_id"])
        if not graph:
            return
        self._view.results_frame.clear()
        for ip in graph.get_hosts():
            ports = merge_sort(graph.get_ports(ip), key=lambda p: p.port)
            for pr in ports:
                self._view.results_frame.add_row(
                    ip, pr.port, pr.state, pr.service, pr.response_ms
                )
        self._view.status_bar.set_status(
            f"Loaded scan: {latest['job_id']} | Target: {latest['target']} | {latest['timestamp']}"
        )
