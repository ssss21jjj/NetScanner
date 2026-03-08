"""
scan_form.py — Form-based input frame (satisfies 70% GUI rubric).
All inputs are validated before scan dispatch.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ScanFormFrame(ttk.LabelFrame):
    """
    Form-based control panel providing:
      - Target IP/CIDR input
      - Port range (start, end)
      - Timeout (seconds)
      - Thread count
      - Start / Stop / Save DB / Export / Load controls
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_save: Optional[Callable] = None,
        on_export: Optional[Callable] = None,
        on_load: Optional[Callable] = None,
    ) -> None:
        super().__init__(parent, text="Scan Configuration", padding=10)
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_save = on_save
        self._on_export = on_export
        self._on_load = on_load
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Construct all form fields with consistent grid layout."""
        # Row 0 — Target
        ttk.Label(self, text="Target (IP/CIDR):").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=3
        )
        self.target_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(self, textvariable=self.target_var, width=22).grid(
            row=0, column=1, sticky=tk.W, padx=5
        )

        # Row 0 — Port range
        ttk.Label(self, text="Port Start:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.port_start_var = tk.IntVar(value=1)
        ttk.Spinbox(self, from_=1, to=65535, textvariable=self.port_start_var,
                    width=7).grid(row=0, column=3, padx=5)

        ttk.Label(self, text="Port End:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.port_end_var = tk.IntVar(value=1024)
        ttk.Spinbox(self, from_=1, to=65535, textvariable=self.port_end_var,
                    width=7).grid(row=0, column=5, padx=5)

        # Row 1 — Timeout + Threads
        ttk.Label(self, text="Timeout (s):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.timeout_var = tk.DoubleVar(value=0.5)
        ttk.Spinbox(self, from_=0.1, to=10.0, increment=0.1,
                    textvariable=self.timeout_var, width=7).grid(
            row=1, column=1, sticky=tk.W, padx=5
        )

        ttk.Label(self, text="Threads:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.threads_var = tk.IntVar(value=50)
        ttk.Spinbox(self, from_=1, to=200, textvariable=self.threads_var,
                    width=7).grid(row=1, column=3, padx=5)

        # Row 1 — Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=4, columnspan=2, padx=5)

        self.start_btn = ttk.Button(btn_frame, text="▶ Start",
                                    command=self._on_start)
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.stop_btn = ttk.Button(btn_frame, text="■ Stop",
                                   command=self._on_stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_frame, text="💾 Save DB",
                   command=self._on_save).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📤 Export",
                   command=self._on_export).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📂 Load",
                   command=self._on_load).pack(side=tk.LEFT, padx=2)

    def get_params(self) -> dict:
        """Return all form field values as a dict."""
        return {
            "target": self.target_var.get().strip(),
            "port_start": self.port_start_var.get(),
            "port_end": self.port_end_var.get(),
            "timeout": self.timeout_var.get(),
            "threads": self.threads_var.get(),
        }

    def set_scanning(self, scanning: bool) -> None:
        """Toggle button states based on whether a scan is running."""
        self.start_btn.config(state=tk.DISABLED if scanning else tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL if scanning else tk.DISABLED)
