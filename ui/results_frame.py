"""
results_frame.py — Treeview displaying scan results.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk


COLUMNS = ("host", "port", "state", "service", "response_ms")
HEADINGS = ("Host IP", "Port", "State", "Service", "Response (ms)")
WIDTHS   = (140,       60,     70,      120,       110)


class ResultsFrame(ttk.LabelFrame):
    """Scrollable Treeview for displaying PortResult entries."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, text="Scan Results", padding=5)
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Build Treeview with vertical scrollbar."""
        self.tree = ttk.Treeview(
            self, columns=COLUMNS, show="headings", selectmode="browse"
        )
        for col, heading, width in zip(COLUMNS, HEADINGS, WIDTHS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def add_row(self, ip: str, port: int, state: str,
                service: str, response_ms: float) -> None:
        """Append a single result row to the Treeview."""
        self.tree.insert(
            "", tk.END,
            values=(ip, port, state, service, f"{response_ms:.1f}")
        )

    def clear(self) -> None:
        """Remove all rows from the Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
