"""
main_window.py — Root Tkinter window and layout manager.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

from ui.scan_form import ScanFormFrame
from ui.results_frame import ResultsFrame
from ui.status_bar import StatusBar


class MainWindow:
    """
    Root application window.

    Layout:
        ┌──────────────────────────────┐
        │  ScanFormFrame (top)         │
        ├──────────────────────────────┤
        │  ResultsFrame (middle, fill) │
        ├──────────────────────────────┤
        │  StatusBar (bottom)          │
        └──────────────────────────────┘
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("NetScanner — ST5062CEM CW1")
        self.root.geometry("900x620")
        self.root.resizable(True, True)
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct all child frames and wire controller."""
        # Import here to avoid circular imports
        from controller.scan_controller import ScanController

        # Results Treeview (build first so controller can reference it)
        self.results_frame = ResultsFrame(self.root)

        # Status bar (build second so controller can reference it)
        self.status_bar = StatusBar(self.root)

        # Controller (needs results_frame + status_bar to exist)
        self.controller = ScanController(self)

        # Scan form — pass controller callbacks to buttons
        self.scan_form = ScanFormFrame(
            self.root,
            on_start=self.controller.start_scan,
            on_stop=self.controller.stop_scan,
            on_save=self.controller.on_save,
            on_export=self.controller.on_export,
            on_load=self.controller.on_load,
        )

        # Pack in visual order (top → middle → bottom)
        self.scan_form.pack(fill=tk.X, padx=10, pady=(10, 0))
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def show_error(self, title: str, message: str) -> None:
        """Display a modal error dialog."""
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str) -> None:
        """Display a modal info dialog."""
        messagebox.showinfo(title, message)
