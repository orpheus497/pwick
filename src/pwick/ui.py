"""
pwick - GUI implementation using PyQt5.
Provides a desktop interface for the password manager with black/grey/white/red theme.
"""

import sys
import os
import secrets
import string
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QDialog, QFileDialog, QMessageBox, QCheckBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QKeySequence

import pyperclip

from . import vault


# Dark theme stylesheet with black, grey, white, and red accents
DARK_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

QLabel {
    color: #e0e0e0;
    font-size: 12px;
}

QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #c62828;
}

QPushButton:pressed {
    background-color: #c62828;
}

QPushButton#primaryButton {
    background-color: #c62828;
    border: 1px solid #b71c1c;
}

QPushButton#primaryButton:hover {
    background-color: #d32f2f;
}

QPushButton#primaryButton:pressed {
    background-color: #b71c1c;
}

QLineEdit, QTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #c62828;
}

QListWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 4px;
    font-size: 12px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #404040;
}

QListWidget::item:selected {
    background-color: #c62828;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QGroupBox {
    border: 1px solid #404040;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    color: #e0e0e0;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
}

QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #404040;
    border-radius: 3px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #c62828;
    border: 1px solid #b71c1c;
}

QMessageBox {
    background-color: #1a1a1a;
}

QMessageBox QLabel {
    color: #e0e0e0;
}
"""


class WelcomeDialog(QDialog):
    """Initial welcome screen for creating, importing, or opening vaults."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pwick - Password Manager")
        self.setModal(True)
        self.resize(400, 300)
        
        self.result_action = None
        self.vault_path = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Welcome to pwick")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel("Your local-first password manager")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Buttons
        create_btn = QPushButton("Create New Vault")
        create_btn.setObjectName("primaryButton")
        create_btn.clicked.connect(self._on_create)
        layout.addWidget(create_btn)
        
        import_btn = QPushButton("Import Existing Vault")
        import_btn.clicked.connect(self._on_import)
        layout.addWidget(import_btn)
        
        open_btn = QPushButton("Open Existing Vault")
        open_btn.clicked.connect(self._on_open)
        layout.addWidget(open_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _on_create(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Create New Vault", "", "Vault Files (*.vault);;All Files (*)"
        )
        if path:
            if not path.endswith('.vault'):
                path += '.vault'
            self.result_action = 'create'
            self.vault_path = path
            self.accept()
    
    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Vault File", "", "Encrypted Files (*.encrypted *.vault);;All Files (*)"
        )
        if path:
            self.result_action = 'import'
            self.vault_path = path
            self.accept()
    
    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Vault", "", "Vault Files (*.vault);;All Files (*)"
        )
        if path:
            self.result_action = 'open'
            self.vault_path = path
            self.accept()


class MasterPasswordDialog(QDialog):
    """Dialog for entering master password."""
    
    def __init__(self, confirm_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Master Password")
        self.setModal(True)
        self.confirm_mode = confirm_mode
        self.password = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        label = QLabel("Enter Master Password:" if not self.confirm_mode 
                      else "Create Master Password:")
        layout.addWidget(label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Master Password")
        layout.addWidget(self.password_input)
        
        if self.confirm_mode:
            confirm_label = QLabel("Confirm Master Password:")
            layout.addWidget(confirm_label)
            
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setPlaceholderText("Confirm Password")
            layout.addWidget(self.confirm_input)
        
        warning = QLabel(
            "⚠️ WARNING: Your master password cannot be recovered. "
            "If you forget it, your data will be lost forever."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #c62828; font-size: 10px;")
        layout.addWidget(warning)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _on_ok(self):
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return
        
        if self.confirm_mode:
            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(self, "Error", "Passwords do not match.")
                return
        
        self.password = password
        self.accept()


class EntryDialog(QDialog):
    """Dialog for adding or editing an entry."""
    
    def __init__(self, entry_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Entry" if entry_data else "Add Entry")
        self.setModal(True)
        self.resize(500, 400)
        
        self.entry_data = entry_data or {}
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
        
        # Password field with show/hide and generate
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
        """Generate a strong random password."""
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


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pwick - Password Manager")
        self.resize(900, 600)
        
        self.vault_path: Optional[str] = None
        self.vault_data: Optional[Dict[str, Any]] = None
        self.master_password: Optional[str] = None
        self.current_entry_id: Optional[str] = None
        
        # Clipboard auto-clear timer (30 seconds)
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self._clear_clipboard)
        self.clipboard_timer.setSingleShot(True)
        
        self._setup_ui()
        self._setup_shortcuts()
        self._show_welcome()
    
    def _setup_ui(self):
        """Setup the main UI."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout()
        
        # Left panel - Entry list
        left_panel = QVBoxLayout()
        
        left_header = QHBoxLayout()
        list_label = QLabel("Entries")
        list_label_font = QFont()
        list_label_font.setPointSize(14)
        list_label_font.setBold(True)
        list_label.setFont(list_label_font)
        left_header.addWidget(list_label)
        left_header.addStretch()
        
        add_btn = QPushButton("Add")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self._add_entry)
        left_header.addWidget(add_btn)
        
        left_panel.addLayout(left_header)
        
        self.entry_list = QListWidget()
        self.entry_list.currentItemChanged.connect(self._on_entry_selected)
        left_panel.addWidget(self.entry_list)
        
        main_layout.addLayout(left_panel, 2)
        
        # Right panel - Entry details
        right_panel = QVBoxLayout()
        
        details_label = QLabel("Details")
        details_label_font = QFont()
        details_label_font.setPointSize(14)
        details_label_font.setBold(True)
        details_label.setFont(details_label_font)
        right_panel.addWidget(details_label)
        
        details_group = QGroupBox()
        details_layout = QFormLayout()
        
        self.detail_title = QLabel("-")
        details_layout.addRow("Title:", self.detail_title)
        
        self.detail_username = QLabel("-")
        details_layout.addRow("Username:", self.detail_username)
        
        password_layout = QHBoxLayout()
        self.detail_password = QLabel("••••••••")
        password_layout.addWidget(self.detail_password)
        password_layout.addStretch()
        details_layout.addRow("Password:", password_layout)
        
        self.detail_notes = QLabel("-")
        self.detail_notes.setWordWrap(True)
        details_layout.addRow("Notes:", self.detail_notes)
        
        details_group.setLayout(details_layout)
        right_panel.addWidget(details_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._edit_entry)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_entry)
        action_layout.addWidget(delete_btn)
        
        copy_btn = QPushButton("Copy Password")
        copy_btn.setObjectName("primaryButton")
        copy_btn.clicked.connect(self._copy_password)
        action_layout.addWidget(copy_btn)
        
        right_panel.addLayout(action_layout)
        
        right_panel.addStretch()
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export Vault")
        export_btn.clicked.connect(self._export_vault)
        bottom_layout.addWidget(export_btn)
        
        bottom_layout.addStretch()
        
        lock_btn = QPushButton("Lock")
        lock_btn.clicked.connect(self._lock_vault)
        bottom_layout.addWidget(lock_btn)
        
        right_panel.addLayout(bottom_layout)
        
        main_layout.addLayout(right_panel, 3)
        
        central.setLayout(main_layout)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        from PyQt5.QtWidgets import QShortcut
        
        # Ctrl+C / Cmd+C - Copy password
        copy_shortcut = QShortcut(QKeySequence.Copy, self)
        copy_shortcut.activated.connect(self._copy_password)
        
        # Ctrl+N / Cmd+N - Add new entry
        new_shortcut = QShortcut(QKeySequence.New, self)
        new_shortcut.activated.connect(self._add_entry)
        
        # Ctrl+E / Cmd+E - Edit entry
        edit_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        edit_shortcut.activated.connect(self._edit_entry)
        
        # Delete - Delete entry
        delete_shortcut = QShortcut(QKeySequence.Delete, self)
        delete_shortcut.activated.connect(self._delete_entry)
        
        # Ctrl+L / Cmd+L - Lock vault
        lock_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        lock_shortcut.activated.connect(self._lock_vault)
        
        # Ctrl+F / Cmd+F - Focus search (if entry list is a search target)
        focus_shortcut = QShortcut(QKeySequence.Find, self)
        focus_shortcut.activated.connect(lambda: self.entry_list.setFocus())
    
    def _clear_clipboard(self):
        """Clear the clipboard for security."""
        pyperclip.copy('')
        self.statusBar().showMessage("Clipboard cleared for security", 2000)
    
    def _show_welcome(self):
        """Show welcome dialog."""
        dialog = WelcomeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            action = dialog.result_action
            path = dialog.vault_path
            
            if action == 'create':
                self._create_vault(path)
            elif action == 'import':
                self._import_vault(path)
            elif action == 'open':
                self._open_vault(path)
        else:
            sys.exit(0)
    
    def _create_vault(self, path: str):
        """Create a new vault."""
        password_dialog = MasterPasswordDialog(confirm_mode=True, parent=self)
        if password_dialog.exec_() == QDialog.Accepted:
            try:
                self.vault_data = vault.create_vault(path, password_dialog.password)
                self.vault_path = path
                self.master_password = password_dialog.password
                self._refresh_entry_list()
                QMessageBox.information(self, "Success", "Vault created successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create vault: {e}")
                self._show_welcome()
        else:
            self._show_welcome()
    
    def _import_vault(self, source_path: str):
        """Import an existing vault."""
        password_dialog = MasterPasswordDialog(parent=self)
        if password_dialog.exec_() == QDialog.Accepted:
            target_path, _ = QFileDialog.getSaveFileName(
                self, "Save Imported Vault As", "", "Vault Files (*.vault);;All Files (*)"
            )
            if target_path:
                if not target_path.endswith('.vault'):
                    target_path += '.vault'
                try:
                    self.vault_data = vault.import_encrypted(
                        source_path, target_path, password_dialog.password
                    )
                    self.vault_path = target_path
                    self.master_password = password_dialog.password
                    self._refresh_entry_list()
                    QMessageBox.information(self, "Success", "Vault imported successfully!")
                except vault.VaultAuthenticationError:
                    QMessageBox.critical(self, "Error", "Incorrect master password.")
                    self._show_welcome()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to import vault: {e}")
                    self._show_welcome()
            else:
                self._show_welcome()
        else:
            self._show_welcome()
    
    def _open_vault(self, path: str):
        """Open an existing vault."""
        password_dialog = MasterPasswordDialog(parent=self)
        if password_dialog.exec_() == QDialog.Accepted:
            try:
                self.vault_data = vault.load_vault(path, password_dialog.password)
                self.vault_path = path
                self.master_password = password_dialog.password
                self._refresh_entry_list()
            except vault.VaultAuthenticationError:
                QMessageBox.critical(self, "Error", "Incorrect master password.")
                self._show_welcome()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open vault: {e}")
                self._show_welcome()
        else:
            self._show_welcome()
    
    def _refresh_entry_list(self):
        """Refresh the entry list."""
        self.entry_list.clear()
        if self.vault_data:
            for entry in self.vault_data['entries']:
                item = QListWidgetItem(entry['title'])
                item.setData(Qt.UserRole, entry['id'])
                self.entry_list.addItem(item)
    
    def _on_entry_selected(self, current, previous):
        """Handle entry selection."""
        if current:
            entry_id = current.data(Qt.UserRole)
            self.current_entry_id = entry_id
            entry = self._find_entry(entry_id)
            if entry:
                self.detail_title.setText(entry['title'])
                self.detail_username.setText(entry['username'] or "-")
                self.detail_password.setText("••••••••")
                self.detail_notes.setText(entry['notes'] or "-")
        else:
            self.current_entry_id = None
            self.detail_title.setText("-")
            self.detail_username.setText("-")
            self.detail_password.setText("••••••••")
            self.detail_notes.setText("-")
    
    def _find_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Find an entry by ID."""
        if self.vault_data:
            for entry in self.vault_data['entries']:
                if entry['id'] == entry_id:
                    return entry
        return None
    
    def _add_entry(self):
        """Add a new entry."""
        dialog = EntryDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.result_data
            vault.add_entry(
                self.vault_data,
                data['title'],
                data['username'],
                data['password'],
                data['notes']
            )
            self._save_vault()
            self._refresh_entry_list()
    
    def _edit_entry(self):
        """Edit the selected entry."""
        if not self.current_entry_id:
            QMessageBox.warning(self, "Warning", "Please select an entry to edit.")
            return
        
        entry = self._find_entry(self.current_entry_id)
        if entry:
            dialog = EntryDialog(entry_data=entry, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.result_data
                vault.update_entry(
                    self.vault_data,
                    self.current_entry_id,
                    data['title'],
                    data['username'],
                    data['password'],
                    data['notes']
                )
                self._save_vault()
                self._refresh_entry_list()
                # Re-select the entry to update details
                for i in range(self.entry_list.count()):
                    item = self.entry_list.item(i)
                    if item.data(Qt.UserRole) == self.current_entry_id:
                        self.entry_list.setCurrentItem(item)
                        break
    
    def _delete_entry(self):
        """Delete the selected entry."""
        if not self.current_entry_id:
            QMessageBox.warning(self, "Warning", "Please select an entry to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this entry?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            vault.delete_entry(self.vault_data, self.current_entry_id)
            self._save_vault()
            self._refresh_entry_list()
            self.current_entry_id = None
    
    def _copy_password(self):
        """Copy the selected entry's password to clipboard."""
        if not self.current_entry_id:
            QMessageBox.warning(self, "Warning", "Please select an entry to copy password.")
            return
        
        entry = self._find_entry(self.current_entry_id)
        if entry:
            pyperclip.copy(entry['password'])
            
            # Start clipboard auto-clear timer (30 seconds)
            self.clipboard_timer.start(30000)  # 30 seconds in milliseconds
            
            # Show temporary notification
            self.statusBar().showMessage("Password copied to clipboard! (Will auto-clear in 30s)", 3000)
    
    def _export_vault(self):
        """Export the vault to an encrypted file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Vault", "", "Encrypted Files (*.encrypted);;All Files (*)"
        )
        if path:
            if not path.endswith('.encrypted'):
                path += '.encrypted'
            try:
                vault.export_encrypted(self.vault_path, path, self.master_password)
                QMessageBox.information(self, "Success", "Vault exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export vault: {e}")
    
    def _lock_vault(self):
        """Lock the vault and return to welcome screen."""
        self.vault_data = None
        self.vault_path = None
        self.master_password = None
        self.current_entry_id = None
        self.entry_list.clear()
        self._show_welcome()
    
    def _save_vault(self):
        """Save the current vault."""
        try:
            vault.save_vault(self.vault_path, self.vault_data, self.master_password)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save vault: {e}")


def run():
    """Run the application."""
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
