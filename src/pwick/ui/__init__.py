"""
pwick.ui - User interface package for pwick password manager.

This package contains the main window and all UI components including
dialogs and widgets for the PySide6-based desktop interface.
"""

from .main_window import MainWindow, run

__all__ = ["MainWindow", "run"]
