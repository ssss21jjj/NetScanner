"""
main.py — Entry point for NetScanner application.
ST5062CEM Programming and Algorithm 2 — CW1
"""

import tkinter as tk
from ui.main_window import MainWindow


def main() -> None:
    """Initialise Tkinter root and launch the application."""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
