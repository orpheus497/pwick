"""
Entry dialog for pwick.
"""

import secrets
import string
from datetime import datetime, timezone
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QCheckBox,
    QMessageBox,
    QLabel,
    QCompleter,
    QWidget,
)
from PySide6.QtCore import Qt, Signal


class TagChip(QWidget):
    """A removable tag chip widget."""

    removed = Signal(str)  # Signal emitted when tag is removed

    def __init__(self, tag: str, parent=None):
        super().__init__(parent)
        self.tag = tag

        layout = QHBoxLayout()
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        label = QLabel(tag)
        label.setStyleSheet("color: #e0e0e0; font-size: 11px;")
        layout.addWidget(label)

        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #c62828;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """
        )
        remove_btn.clicked.connect(lambda: self.removed.emit(self.tag))
        layout.addWidget(remove_btn)

        self.setLayout(layout)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #404040;
                border-radius: 10px;
                padding: 2px;
            }
        """
        )


class EntryDialog(QDialog):
    """Dialog for adding or editing an entry."""

    def __init__(
        self,
        entry_data=None,
        settings=None,
        all_tags: Optional[List[str]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Edit Entry" if entry_data else "Add Entry")
        self.setModal(True)
        self.resize(500, 500)

        self.entry_data = entry_data or {}
        self.settings = settings
        self.all_tags = all_tags or []
        self.result_data = None
        self.current_tags: List[str] = list(self.entry_data.get("tags", []))

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        form = QFormLayout()

        # Title
        self.title_input = QLineEdit()
        self.title_input.setMaxLength(256)  # Security: prevent memory exhaustion
        self.title_input.setText(self.entry_data.get("title", ""))
        form.addRow("Title:", self.title_input)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setMaxLength(256)  # Security: prevent memory exhaustion
        self.username_input.setText(self.entry_data.get("username", ""))
        form.addRow("Username:", self.username_input)

        # Password with show/generate
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setMaxLength(
            1024
        )  # Security: prevent memory exhaustion (allows long passphrases)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.entry_data.get("password", ""))
        password_layout.addWidget(self.password_input)

        self.show_password_check = QCheckBox("Show")
        self.show_password_check.stateChanged.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.show_password_check)

        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self._generate_password)
        password_layout.addWidget(generate_btn)

        form.addRow("Password:", password_layout)

        # Password age (if editing existing entry)
        if self.entry_data and "last_password_change" in self.entry_data:
            age_text = self._calculate_password_age()
            age_label = QLabel(age_text)
            age_label.setStyleSheet("color: #888888; font-size: 11px;")
            form.addRow("Password Age:", age_label)

        # Tags
        tags_container = QWidget()
        tags_layout = QVBoxLayout()
        tags_layout.setContentsMargins(0, 0, 0, 0)

        # Tag input with autocomplete
        tag_input_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setMaxLength(50)  # Security: prevent memory exhaustion
        self.tag_input.setPlaceholderText("Add tag...")
        self.tag_input.returnPressed.connect(self._add_tag)

        # Autocomplete from existing tags
        if self.all_tags:
            completer = QCompleter(self.all_tags)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.tag_input.setCompleter(completer)

        tag_input_layout.addWidget(self.tag_input)

        add_tag_btn = QPushButton("Add Tag")
        add_tag_btn.clicked.connect(self._add_tag)
        tag_input_layout.addWidget(add_tag_btn)

        tags_layout.addLayout(tag_input_layout)

        # Tag chips display
        self.tags_display = QWidget()
        self.tags_display_layout = QHBoxLayout()
        self.tags_display_layout.setContentsMargins(0, 5, 0, 5)
        self.tags_display.setLayout(self.tags_display_layout)
        tags_layout.addWidget(self.tags_display)

        tags_container.setLayout(tags_layout)
        form.addRow("Tags:", tags_container)

        # Refresh tag display
        self._refresh_tag_display()

        # Pin checkbox
        self.pin_checkbox = QCheckBox("Pin this entry (show at top of list)")
        self.pin_checkbox.setChecked(self.entry_data.get("pinned", False))
        form.addRow("", self.pin_checkbox)

        # Notes with character counter
        notes_container = QWidget()
        notes_layout = QVBoxLayout()
        notes_layout.setContentsMargins(0, 0, 0, 0)

        self.notes_input = QTextEdit()
        self.notes_input.setText(self.entry_data.get("notes", ""))
        self.notes_input.setMaximumHeight(100)
        self.notes_input.textChanged.connect(self._update_notes_counter)
        notes_layout.addWidget(self.notes_input)

        # Character counter
        self.notes_counter = QLabel()
        self.notes_counter.setStyleSheet("color: #888888; font-size: 10px;")
        notes_layout.addWidget(self.notes_counter)

        notes_container.setLayout(notes_layout)
        form.addRow("Notes:", notes_container)

        # Initialize counter
        self._update_notes_counter()

        layout.addLayout(form)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def _generate_password(self):
        if self.settings:
            length = self.settings["password_generator_length"]
            chars = ""
            if self.settings["password_generator_use_uppercase"]:
                chars += string.ascii_uppercase
            if self.settings["password_generator_use_lowercase"]:
                chars += string.ascii_lowercase
            if self.settings["password_generator_use_digits"]:
                chars += string.digits
            if self.settings["password_generator_use_punctuation"]:
                chars += string.punctuation

            if not chars:  # Fallback if no character sets selected
                chars = string.ascii_letters + string.digits + string.punctuation
        else:
            # Fallback to defaults if no settings available
            length = 20
            chars = string.ascii_letters + string.digits + string.punctuation

        password = "".join(secrets.choice(chars) for _ in range(length))
        self.password_input.setText(password)
        self.show_password_check.setChecked(True)

    def _calculate_password_age(self) -> str:
        """Calculate how long since password was last changed."""
        last_change = self.entry_data.get("last_password_change")
        if not last_change:
            return "Unknown"

        try:
            last_change_dt = datetime.fromisoformat(last_change.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            delta = now - last_change_dt
            days = delta.days

            if days == 0:
                return "Changed today"
            elif days == 1:
                return "1 day old"
            elif days < 30:
                return f"{days} days old"
            elif days < 365:
                months = days // 30
                return f"{months} month{'s' if months > 1 else ''} old"
            else:
                years = days // 365
                return f"{years} year{'s' if years > 1 else ''} old"
        except Exception:
            return "Unknown"

    def _add_tag(self):
        """Add a tag from the input field."""
        tag = self.tag_input.text().strip()

        # Security: validate tag length (already enforced by setMaxLength, but double-check)
        if len(tag) > 50:
            QMessageBox.warning(
                self, "Tag Too Long", "Tags must be 50 characters or less."
            )
            return

        # Security: validate tag count
        if len(self.current_tags) >= 50:
            QMessageBox.warning(self, "Too Many Tags", "Maximum 50 tags per entry.")
            return

        if tag and tag not in self.current_tags:
            self.current_tags.append(tag)
            self._refresh_tag_display()
            self.tag_input.clear()
        elif tag in self.current_tags:
            QMessageBox.information(
                self, "Duplicate Tag", f"Tag '{tag}' already added."
            )

    def _remove_tag(self, tag: str):
        """Remove a tag from the current tags list."""
        if tag in self.current_tags:
            self.current_tags.remove(tag)
            self._refresh_tag_display()

    def _refresh_tag_display(self):
        """Refresh the tag chips display."""
        # Clear existing chips
        while self.tags_display_layout.count():
            item = self.tags_display_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add chip for each tag
        for tag in self.current_tags:
            chip = TagChip(tag)
            chip.removed.connect(self._remove_tag)
            self.tags_display_layout.addWidget(chip)

        # Add stretch to left-align chips
        self.tags_display_layout.addStretch()

    def _update_notes_counter(self):
        """Update the notes character counter."""
        current_length = len(self.notes_input.toPlainText())
        max_length = 10000

        # Security: enforce maximum notes length
        if current_length > max_length:
            # Truncate to max length
            cursor = self.notes_input.textCursor()
            position = cursor.position()
            self.notes_input.setPlainText(self.notes_input.toPlainText()[:max_length])
            # Restore cursor position (or move to end if it was beyond max)
            cursor.setPosition(min(position, max_length))
            self.notes_input.setTextCursor(cursor)
            current_length = max_length

        # Update counter text with color coding
        self.notes_counter.setText(f"{current_length:,} / {max_length:,} characters")
        if current_length > max_length * 0.9:
            self.notes_counter.setStyleSheet(
                "color: #ff6b6b; font-size: 10px;"
            )  # Red when near limit
        elif current_length > max_length * 0.75:
            self.notes_counter.setStyleSheet(
                "color: #ffa500; font-size: 10px;"
            )  # Orange
        else:
            self.notes_counter.setStyleSheet("color: #888888; font-size: 10px;")  # Gray

    def _on_save(self):
        title = self.title_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        notes = self.notes_input.toPlainText().strip()
        pinned = self.pin_checkbox.isChecked()

        # Validation: title required
        if not title:
            QMessageBox.warning(self, "Validation Error", "Title is required.")
            return

        # Security: validate lengths (belt-and-suspenders approach)
        if len(title) > 256:
            QMessageBox.warning(
                self, "Validation Error", "Title is too long (maximum 256 characters)."
            )
            return

        if len(username) > 256:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Username is too long (maximum 256 characters).",
            )
            return

        if len(password) > 1024:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Password is too long (maximum 1024 characters).",
            )
            return

        if len(notes) > 10000:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Notes are too long (maximum 10,000 characters).",
            )
            return

        # Security: validate tags
        for tag in self.current_tags:
            if len(tag) > 50:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    f"Tag '{tag[:20]}...' is too long (maximum 50 characters).",
                )
                return

        if len(self.current_tags) > 50:
            QMessageBox.warning(
                self, "Validation Error", "Too many tags (maximum 50 tags per entry)."
            )
            return

        self.result_data = {
            "title": title,
            "username": username,
            "password": password,
            "notes": notes,
            "tags": self.current_tags,
            "pinned": pinned,
        }

        self.accept()
