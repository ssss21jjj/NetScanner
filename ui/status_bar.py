"""
status_bar.py — Bottom status bar with progress indicator.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk


class StatusBar(ttk.Frame):
    """
    Bottom frame containing:
    - A ttk.Progressbar (determinate or indeterminate)
    - A status label showing current operation
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, relief=tk.SUNKEN, padding=(5, 2))
        self._build_widgets()

    def _build_widgets(self) -> None:
        self.status_var = tk.StringVar(value="Ready")
        self.label = ttk.Label(self, textvariable=self.status_var, anchor=tk.W)
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress = ttk.Progressbar(
            self, orient=tk.HORIZONTAL, length=200, mode="indeterminate"
        )
        self.progress.pack(side=tk.RIGHT, padx=5)

    def set_status(self, message: str) -> None:
        """Update status label text."""
        self.status_var.set(message)

    def start_progress(self) -> None:
        """Begin indeterminate progress animation."""
        self.progress.start(10)

    def stop_progress(self) -> None:
        """Stop progress animation and reset."""
        self.progress.stop()
        self.progress["value"] = 0
