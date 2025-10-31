"""
Entry dialog for pwick.
"""

import secrets
import string

from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QCheckBox, QMessageBox
from PySide6.QtCore import Qt


class EntryDialog(QDialog):
    """Dialog for adding or editing an entry."""

    def __init__(self, entry_data=None, settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Entry" if entry_data else "Add Entry")
        self.setModal(True)
        self.resize(500, 400)

        self.entry_data = entry_data or {}
        self.settings = settings
        self.result_data = None

        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setText(self.entry_data.get('title', ''))
        form.addRow("Title:", self.title_input)
        
        self.username_input = QLineEdit()
        self.username_input.setText(self.entry_data.get('username', ''))
        form.addRow("Username:", self.username_input)
        
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.entry_data.get('password', ''))
        password_layout.addWidget(self.password_input)
        
        self.show_password_check = QCheckBox("Show")
        self.show_password_check.stateChanged.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.show_password_check)
        
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self._generate_password)
        password_layout.addWidget(generate_btn)
        
        form.addRow("Password:", password_layout)
        
        self.notes_input = QTextEdit()
        self.notes_input.setText(self.entry_data.get('notes', ''))
        self.notes_input.setMaximumHeight(100)
        form.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form)
        
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
            length = self.settings['password_generator_length']
            chars = ''
            if self.settings['password_generator_use_uppercase']:
                chars += string.ascii_uppercase
            if self.settings['password_generator_use_lowercase']:
                chars += string.ascii_lowercase
            if self.settings['password_generator_use_digits']:
                chars += string.digits
            if self.settings['password_generator_use_punctuation']:
                chars += string.punctuation

            if not chars:  # Fallback if no character sets selected
                chars = string.ascii_letters + string.digits + string.punctuation
        else:
            # Fallback to defaults if no settings available
            length = 20
            chars = string.ascii_letters + string.digits + string.punctuation

        password = ''.join(secrets.choice(chars) for _ in range(length))
        self.password_input.setText(password)
        self.show_password_check.setChecked(True)
    
    def _on_save(self):
        title = self.title_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        notes = self.notes_input.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Error", "Title is required.")
            return
        
        self.result_data = {
            'title': title,
            'username': username,
            'password': password,
            'notes': notes
        }
        
        self.accept()
