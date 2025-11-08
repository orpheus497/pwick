"""
Command Palette Dialog for pwick.

Provides a quick command launcher similar to VS Code's command palette.
Press Ctrl+K to open and quickly access any function.
"""

from __future__ import annotations

from typing import Callable, List, Tuple, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence


class CommandPaletteDialog(QDialog):
    """
    Command Palette for quick access to all application functions.

    Provides fuzzy search and keyboard navigation for rapid command execution.
    """

    command_selected = Signal(str)

    def __init__(self, parent=None):
        """
        Initialize the Command Palette.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.commands: List[Tuple[str, str, Callable]] = []

        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.resize(600, 400)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the palette UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type a command... (Esc to cancel)")
        self.search_box.textChanged.connect(self._filter_commands)
        self.search_box.returnPressed.connect(self._execute_selected)
        layout.addWidget(self.search_box)

        # Command list
        self.command_list = QListWidget()
        self.command_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.command_list)

        self.setLayout(layout)

        # Set focus to search box
        self.search_box.setFocus()

    def add_command(self, name: str, description: str, callback: Callable):
        """
        Add a command to the palette.

        Args:
            name: Command name (shown in palette)
            description: Command description
            callback: Function to call when command is executed
        """
        self.commands.append((name, description, callback))

    def clear_commands(self):
        """Clear all commands from the palette."""
        self.commands.clear()
        self.command_list.clear()

    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        self._refresh_command_list()
        self.search_box.clear()
        self.search_box.setFocus()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Down:
            self.command_list.setFocus()
            if self.command_list.count() > 0:
                self.command_list.setCurrentRow(0)
        elif event.key() == Qt.Key_Up:
            self.command_list.setFocus()
            if self.command_list.count() > 0:
                self.command_list.setCurrentRow(self.command_list.count() - 1)
        else:
            super().keyPressEvent(event)

    def _refresh_command_list(self):
        """Refresh the full command list."""
        self.command_list.clear()

        for name, description, _ in self.commands:
            item = QListWidgetItem(f"{name}\n  {description}")
            item.setData(Qt.UserRole, name)
            self.command_list.addItem(item)

    def _filter_commands(self, search_text: str):
        """
        Filter commands based on search text.

        Uses fuzzy matching to find commands.
        """
        search_text = search_text.lower()
        self.command_list.clear()

        if not search_text:
            self._refresh_command_list()
            return

        # Fuzzy search
        for name, description, _ in self.commands:
            # Simple fuzzy matching: check if all search chars appear in order
            if self._fuzzy_match(search_text, name.lower()):
                item = QListWidgetItem(f"{name}\n  {description}")
                item.setData(Qt.UserRole, name)
                self.command_list.addItem(item)

        # Auto-select first item
        if self.command_list.count() > 0:
            self.command_list.setCurrentRow(0)

    def _fuzzy_match(self, search: str, text: str) -> bool:
        """
        Check if search characters appear in text in order.

        Args:
            search: Search string
            text: Text to search in

        Returns:
            True if all characters in search appear in text in order
        """
        search_idx = 0
        text_idx = 0

        while search_idx < len(search) and text_idx < len(text):
            if search[search_idx] == text[text_idx]:
                search_idx += 1
            text_idx += 1

        return search_idx == len(search)

    def _execute_selected(self):
        """Execute the currently selected command."""
        current_item = self.command_list.currentItem()
        if current_item:
            command_name = current_item.data(Qt.UserRole)
            self._execute_command(command_name)

    def _on_item_double_clicked(self, item):
        """Handle double-click on command item."""
        command_name = item.data(Qt.UserRole)
        self._execute_command(command_name)

    def _execute_command(self, command_name: str):
        """
        Execute a command by name.

        Args:
            command_name: Name of command to execute
        """
        for name, _, callback in self.commands:
            if name == command_name:
                self.accept()  # Close dialog
                callback()  # Execute command
                break


def create_command_palette(main_window) -> CommandPaletteDialog:
    """
    Create and populate a command palette for the main window.

    Args:
        main_window: Main window instance

    Returns:
        Configured CommandPaletteDialog
    """
    palette = CommandPaletteDialog(main_window)

    # File operations
    palette.add_command(
        "Create New Vault",
        "Create a new encrypted vault file",
        main_window._show_welcome
    )
    palette.add_command(
        "Lock Vault",
        "Lock the current vault",
        main_window._lock_vault
    )
    palette.add_command(
        "Export Vault",
        "Export vault to encrypted file",
        main_window._export_vault
    )

    # Password operations
    palette.add_command(
        "Add Password",
        "Add a new password entry",
        main_window._add_password_entry
    )
    palette.add_command(
        "Edit Password",
        "Edit the selected password entry",
        main_window._edit_password_entry
    )
    palette.add_command(
        "Delete Password",
        "Delete the selected password entry",
        main_window._delete_password_entry
    )
    palette.add_command(
        "Copy Password",
        "Copy selected password to clipboard",
        main_window._copy_password
    )

    # Note operations
    palette.add_command(
        "Add Note",
        "Add a new note entry",
        main_window._add_note_entry
    )
    palette.add_command(
        "Save Note",
        "Save the current note",
        main_window._save_note_entry
    )
    palette.add_command(
        "Delete Note",
        "Delete the selected note entry",
        main_window._delete_note_entry
    )

    # Tools
    palette.add_command(
        "Security Audit",
        "Run security audit to find weak/duplicate passwords",
        main_window._run_security_audit
    )
    palette.add_command(
        "Tag Manager",
        "Manage tags (rename, merge, delete)",
        main_window._open_tag_manager
    )
    palette.add_command(
        "Settings",
        "Open settings dialog",
        main_window._open_settings
    )
    palette.add_command(
        "Clear Clipboard",
        "Clear clipboard immediately",
        main_window._clear_clipboard
    )

    # View operations
    palette.add_command(
        "Show Passwords Tab",
        "Switch to passwords view",
        lambda: main_window.tabs.setCurrentIndex(0)
    )
    palette.add_command(
        "Show Notes Tab",
        "Switch to notes view",
        lambda: main_window.tabs.setCurrentIndex(1)
    )
    palette.add_command(
        "Focus Search",
        "Focus the search box",
        lambda: (main_window.search_passwords.setFocus() if main_window.tabs.currentIndex() == 0
                else main_window.search_notes.setFocus())
    )

    return palette
