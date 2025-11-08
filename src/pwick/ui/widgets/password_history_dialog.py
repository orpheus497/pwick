"""
Password history dialog for pwick.

Displays the password history for an entry, allowing users to view and copy
previous passwords if needed.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
import pyperclip


class PasswordHistoryDialog(QDialog):
    """
    Dialog that displays password history for an entry.

    Shows list of previous passwords with timestamps and allows copying.
    """

    def __init__(self, entry, encrypted_clipboard, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.encrypted_clipboard = encrypted_clipboard

        self.setWindowTitle(f"Password History - {entry['title']}")
        self.setModal(True)
        self.resize(600, 400)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel(
            f"Password history for: <b>{self.entry['title']}</b>\n\n"
            "Below are the previous passwords for this entry. You can copy them if needed,\n"
            "but be aware that old passwords may no longer be secure."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Password history list
        history = self.entry.get('password_history', [])

        if not history:
            no_history = QLabel("No password history available for this entry.\n\n"
                               "Password history is recorded when you update a password.")
            no_history.setAlignment(Qt.AlignCenter)
            no_history.setStyleSheet("color: #999; font-size: 12px; padding: 20px;")
            layout.addWidget(no_history)

            # Close button
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            close_btn = QPushButton("Close")
            close_btn.setObjectName("primaryButton")
            close_btn.clicked.connect(self.accept)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)
        else:
            list_label = QLabel(f"Previous passwords ({len(history)}):")
            layout.addWidget(list_label)

            self.history_list = QListWidget()
            self.history_list.itemDoubleClicked.connect(self._on_item_double_clicked)

            for hist_item in history:
                password = hist_item.get('password', '')
                changed_at = hist_item.get('changed_at', 'Unknown date')

                # Mask password for display
                masked = '•' * len(password) if password else '(empty)'

                # Format date for display
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(changed_at.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date_str = changed_at

                item_text = f"{date_str} - {masked} ({len(password)} chars)"

                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, password)  # Store actual password
                self.history_list.addItem(item)

            layout.addWidget(self.history_list)

            hint_label = QLabel("💡 Tip: Double-click an entry to copy that password")
            hint_label.setStyleSheet("color: #999; font-size: 10px; font-style: italic;")
            layout.addWidget(hint_label)

            # Buttons
            button_layout = QHBoxLayout()

            copy_btn = QPushButton("Copy Selected")
            copy_btn.clicked.connect(self._copy_selected)
            button_layout.addWidget(copy_btn)

            button_layout.addStretch()

            close_btn = QPushButton("Close")
            close_btn.setObjectName("primaryButton")
            close_btn.clicked.connect(self.accept)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

        self.setLayout(layout)

    def _copy_selected(self):
        """Copy the selected password from history."""
        current_item = self.history_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a password from the history list.")
            return

        self._copy_password(current_item)

    def _on_item_double_clicked(self, item):
        """Handle double-click on history item."""
        self._copy_password(item)

    def _copy_password(self, item):
        """Copy password from history item to clipboard."""
        password = item.data(Qt.UserRole)

        if not password:
            QMessageBox.warning(self, "Empty Password", "This historical password is empty.")
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Copy Old Password",
            "You are about to copy an old password to the clipboard.\n\n"
            "⚠️ Warning: This password may no longer be secure or in use.\n\n"
            "Are you sure you want to copy it?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Encrypt and copy to clipboard with error handling
            try:
                self.encrypted_clipboard.copy_encrypted(password)
                QMessageBox.information(
                    self,
                    "Password Copied",
                    "Old password has been copied to clipboard (encrypted).\n"
                    "It will be automatically cleared in 30 seconds."
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Clipboard Error",
                    f"Could not access system clipboard.\n\n"
                    f"Error: {e}\n\n"
                    f"On Linux, install clipboard support:\n"
                    f"  Ubuntu/Debian: sudo apt install xclip\n"
                    f"  Fedora: sudo dnf install xclip\n"
                    f"  Arch: sudo pacman -S xclip"
                )
