"""
pwick - GUI implementation using PySide6.
Provides a desktop interface for the password manager with a dark theme.
"""

from __future__ import annotations

import sys
import secrets
import base64
from typing import Optional, Dict, List
from datetime import datetime, date

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QSystemTrayIcon,
    QMenu,
    QTabWidget,
    QInputDialog,
    QComboBox,
)
from PySide6.QtCore import Qt, QTimer, QKeyCombination
from PySide6.QtGui import (
    QFont,
    QKeySequence,
    QIcon,
    QPixmap,
    QPainter,
    QColor,
    QAction,
    QShortcut,
)

import pyperclip
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import csv

from .. import vault
from ..config import load_settings
from ..logging_config import setup_logging, get_logger
from ..system_theme import get_auto_theme
from .themes import get_stylesheet
from .widgets.welcome_dialog import WelcomeDialog
from .widgets.master_password_dialog import MasterPasswordDialog
from .widgets.entry_dialog import EntryDialog
from .widgets.settings_dialog import SettingsDialog
from .widgets.security_audit_dialog import SecurityAuditDialog
from .widgets.password_history_dialog import PasswordHistoryDialog
from .widgets.tag_manager_dialog import TagManagerDialog
from .widgets.backup_manager_dialog import BackupManagerDialog
from .widgets.import_wizard_dialog import ImportWizardDialog
from .widgets.command_palette_dialog import create_command_palette

# Initialize module logger
logger = get_logger(__name__)


class EncryptedClipboard:
    """
    Encrypted clipboard manager to prevent telemetry and clipboard snooping.
    Encrypts data before placing on system clipboard using AES-256-GCM.
    """

    def __init__(self):
        # Generate a session key for this application instance
        self.session_key = AESGCM.generate_key(bit_length=256)
        self.cipher = AESGCM(self.session_key)
        self.prefix = "PWICK_ENC:"

    def copy_encrypted(self, plaintext: str) -> None:
        """
        Encrypt plaintext and copy to clipboard.
        Format: PWICK_ENC:<base64(nonce||ciphertext||tag)>

        Raises:
            Exception: If clipboard operation fails
        """
        if not plaintext:
            return

        # Generate random nonce
        nonce = secrets.token_bytes(12)

        # Encrypt the plaintext
        ciphertext = self.cipher.encrypt(nonce, plaintext.encode("utf-8"), None)

        # Combine nonce + ciphertext and encode as base64
        encrypted_blob = base64.b64encode(nonce + ciphertext).decode("ascii")

        # Copy to clipboard with prefix (may raise exception if clipboard unavailable)
        try:
            pyperclip.copy(self.prefix + encrypted_blob)
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Clipboard access failed: {e}") from e

    def paste_decrypted(self) -> Optional[str]:
        """
        Retrieve from clipboard and decrypt if it's our encrypted format.
        Returns None if clipboard doesn't contain our encrypted data or decryption fails.
        """
        try:
            clipboard_content = pyperclip.paste()

            if not clipboard_content.startswith(self.prefix):
                # Not our encrypted data, could be from external source
                return None

            # Remove prefix and decode base64
            encrypted_blob = clipboard_content[len(self.prefix) :]
            encrypted_data = base64.b64decode(encrypted_blob)

            # Extract nonce and ciphertext
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]

            # Decrypt
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception:
            # Decryption failed or invalid format
            return None


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.vault_path: Optional[str] = None
        self.vault_data: Optional[vault.Vault] = None
        self.master_password: Optional[str] = None
        self.current_entry_id: Optional[str] = None

        # Load user settings
        self.settings = load_settings()
        self.auto_lock_minutes = self.settings["auto_lock_minutes"]
        self.max_clipboard_history = self.settings["clipboard_history_size"]

        self.encrypted_clipboard = EncryptedClipboard()
        self.clipboard_timer = QTimer()
        self.clipboard_history: List[Dict[str, str]] = []
        self.clipboard_history_date: date = date.today()
        self.auto_lock_timer = QTimer()

        self.setWindowTitle("pwick - Password Manager")
        self.resize(900, 600)

        # Setup system tray
        self._setup_system_tray()

        self._setup_ui()
        self._setup_menu_bar()
        self._setup_shortcuts()

        # Setup command palette
        self.command_palette = create_command_palette(self)

        self._show_welcome()

    def _safe_clipboard_copy(self, text: str, encrypted: bool = True) -> bool:
        """
        Safely copy text to clipboard with error handling.

        Args:
            text: Text to copy
            encrypted: Whether to encrypt before copying (default: True)

        Returns:
            True if successful, False if clipboard operation failed
        """
        try:
            if encrypted:
                self.encrypted_clipboard.copy_encrypted(text)
            else:
                pyperclip.copy(text)
            return True
        except Exception as e:
            logger.warning(f"Clipboard operation failed: {e}")
            QMessageBox.warning(
                self,
                "Clipboard Error",
                f"Could not access system clipboard.\n\n"
                f"Error: {e}\n\n"
                f"On Linux, install clipboard support:\n"
                f"  Ubuntu/Debian: sudo apt install xclip\n"
                f"  Fedora: sudo dnf install xclip\n"
                f"  Arch: sudo pacman -S xclip\n\n"
                f"The password is still available in the entry dialog.",
            )
            return False

    def event(self, event):
        """Reset auto-lock timer on user activity."""
        if self.vault_data and self.auto_lock_minutes > 0:
            self.auto_lock_timer.start(self.auto_lock_minutes * 60 * 1000)
        return super().event(event)

    def _setup_system_tray(self):
        """Setup system tray icon and menu."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(198, 40, 40))
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 40, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "P")
        painter.end()
        icon = QIcon(pixmap)

        self.tray_icon = QSystemTrayIcon(icon, self)
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self._show_from_tray)
        tray_menu.addAction(show_action)

        hide_action = QAction("Hide to Tray", self)
        hide_action.triggered.connect(self._hide_to_tray)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        lock_action = QAction("Lock Vault", self)
        lock_action.triggered.connect(self._lock_vault)
        tray_menu.addAction(lock_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
        self.tray_icon.showMessage(
            "pwick Running",
            "pwick is running in the background. Click the tray icon to show/hide.",
            QSystemTrayIcon.Information,
            2000,
        )

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self._hide_to_tray()
            else:
                self._show_from_tray()

    def _show_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            "pwick Minimized",
            "pwick is running in the background. Double-click the tray icon to restore.",
            QSystemTrayIcon.Information,
            2000,
        )

    def _quit_application(self):
        self.master_password = None
        self.vault_data = None
        self.clipboard_history.clear()  # Clear clipboard history for security
        self._clear_clipboard()
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            event.ignore()
            self._hide_to_tray()
        else:
            event.accept()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Passwords Tab ---
        passwords_tab = QWidget()
        passwords_layout = QHBoxLayout(passwords_tab)

        left_panel = QVBoxLayout()
        left_header = QHBoxLayout()
        list_label = QLabel("Passwords")
        list_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_header.addWidget(list_label)
        left_header.addStretch()
        add_btn = QPushButton("Add Password")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self._add_password_entry)
        left_header.addWidget(add_btn)
        import_csv_btn = QPushButton("Import CSV")
        import_csv_btn.clicked.connect(self._import_csv)
        left_header.addWidget(import_csv_btn)
        left_panel.addLayout(left_header)

        self.search_passwords = QLineEdit()
        self.search_passwords.setPlaceholderText("Search passwords...")
        self.search_passwords.textChanged.connect(self._filter_lists)
        left_panel.addWidget(self.search_passwords)

        # Sorting and filtering controls
        controls_layout = QHBoxLayout()

        sort_label = QLabel("Sort:")
        controls_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(
            [
                "Alphabetical (A-Z)",
                "Alphabetical (Z-A)",
                "Date Created (Newest)",
                "Date Created (Oldest)",
                "Date Modified (Newest)",
                "Date Modified (Oldest)",
            ]
        )
        self.sort_combo.currentIndexChanged.connect(self._refresh_lists)
        controls_layout.addWidget(self.sort_combo)

        controls_layout.addSpacing(10)

        filter_label = QLabel("Filter:")
        controls_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Entries", "Pinned Only", "Unpinned Only"])
        self.filter_combo.currentIndexChanged.connect(self._filter_lists)
        controls_layout.addWidget(self.filter_combo)

        tag_label = QLabel("Tag:")
        controls_layout.addWidget(tag_label)

        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("All Tags")
        self.tag_filter_combo.currentIndexChanged.connect(self._filter_lists)
        controls_layout.addWidget(self.tag_filter_combo)

        controls_layout.addStretch()
        left_panel.addLayout(controls_layout)

        self.entry_list = QListWidget()
        self.entry_list.currentItemChanged.connect(self._on_entry_selected)
        left_panel.addWidget(self.entry_list)
        passwords_layout.addLayout(left_panel, 2)

        right_panel = QVBoxLayout()
        details_label = QLabel("Password Details")
        details_label.setFont(QFont("Arial", 14, QFont.Bold))
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

        clipboard_label = QLabel("Clipboard History (Last 30)")
        clipboard_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_panel.addWidget(clipboard_label)

        self.clipboard_history_list = QListWidget()
        self.clipboard_history_list.setMaximumHeight(150)
        self.clipboard_history_list.itemDoubleClicked.connect(
            self._on_clipboard_history_double_click
        )
        right_panel.addWidget(self.clipboard_history_list)

        action_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._edit_password_entry)
        action_layout.addWidget(edit_btn)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_password_entry)
        action_layout.addWidget(delete_btn)
        history_btn = QPushButton("History")
        history_btn.clicked.connect(self._show_password_history)
        action_layout.addWidget(history_btn)
        copy_btn = QPushButton("Copy Password")
        copy_btn.setObjectName("primaryButton")
        copy_btn.clicked.connect(self._copy_password)
        action_layout.addWidget(copy_btn)
        right_panel.addLayout(action_layout)
        right_panel.addStretch()

        bottom_layout = QHBoxLayout()
        export_btn = QPushButton("Export Vault")
        export_btn.clicked.connect(self._export_vault)
        bottom_layout.addWidget(export_btn)
        bottom_layout.addStretch()
        lock_btn = QPushButton("Lock")
        lock_btn.clicked.connect(self._lock_vault)
        bottom_layout.addWidget(lock_btn)
        right_panel.addLayout(bottom_layout)
        passwords_layout.addLayout(right_panel, 3)
        self.tabs.addTab(passwords_tab, "Passwords")

        # --- Notes Tab ---
        notes_tab = QWidget()
        notes_layout = QHBoxLayout(notes_tab)

        notes_left_panel = QVBoxLayout()
        notes_left_header = QHBoxLayout()
        notes_list_label = QLabel("Notes")
        notes_list_label.setFont(QFont("Arial", 14, QFont.Bold))
        notes_left_header.addWidget(notes_list_label)
        notes_left_header.addStretch()
        add_note_btn = QPushButton("Add Note")
        add_note_btn.setObjectName("primaryButton")
        add_note_btn.clicked.connect(self._add_note_entry)
        notes_left_header.addWidget(add_note_btn)
        notes_left_panel.addLayout(notes_left_header)

        self.search_notes = QLineEdit()
        self.search_notes.setPlaceholderText("Search notes...")
        self.search_notes.textChanged.connect(self._filter_lists)
        notes_left_panel.addWidget(self.search_notes)

        self.note_list = QListWidget()
        self.note_list.currentItemChanged.connect(self._on_entry_selected)
        notes_left_panel.addWidget(self.note_list)
        notes_layout.addLayout(notes_left_panel, 2)

        notes_right_panel = QVBoxLayout()
        notes_details_label = QLabel("Note Details")
        notes_details_label.setFont(QFont("Arial", 14, QFont.Bold))
        notes_right_panel.addWidget(notes_details_label)

        notes_details_group = QGroupBox()
        notes_details_layout = QFormLayout()
        self.note_detail_title = QLineEdit()
        notes_details_layout.addRow("Title:", self.note_detail_title)
        self.note_detail_content = QTextEdit()
        notes_details_layout.addRow("Content:", self.note_detail_content)
        notes_details_group.setLayout(notes_details_layout)
        notes_right_panel.addWidget(notes_details_group)

        note_action_layout = QHBoxLayout()
        save_note_btn = QPushButton("Save Note")
        save_note_btn.setObjectName("primaryButton")
        save_note_btn.clicked.connect(self._save_note_entry)
        note_action_layout.addWidget(save_note_btn)
        delete_note_btn = QPushButton("Delete Note")
        delete_note_btn.clicked.connect(self._delete_note_entry)
        note_action_layout.addWidget(delete_note_btn)
        notes_right_panel.addLayout(note_action_layout)
        notes_right_panel.addStretch()
        notes_layout.addLayout(notes_right_panel, 3)
        self.tabs.addTab(notes_tab, "Notes")

    def _setup_menu_bar(self):
        """Setup the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        import_wizard_action = QAction("Import Wizard...", self)
        import_wizard_action.triggered.connect(self._open_import_wizard)
        file_menu.addAction(import_wizard_action)

        import_csv_action = QAction("Import from CSV...", self)
        import_csv_action.triggered.connect(self._import_csv)
        file_menu.addAction(import_csv_action)

        export_csv_action = QAction("Export to CSV...", self)
        export_csv_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_csv_action)

        file_menu.addSeparator()

        export_vault_action = QAction("Export Vault...", self)
        export_vault_action.triggered.connect(self._export_vault)
        file_menu.addAction(export_vault_action)

        file_menu.addSeparator()

        lock_action = QAction("Lock Vault", self)
        lock_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_L))
        lock_action.triggered.connect(self._lock_vault)
        file_menu.addAction(lock_action)

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self._quit_application)
        file_menu.addAction(quit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        backup_manager_action = QAction("Backup Manager...", self)
        backup_manager_action.triggered.connect(self._open_backup_manager)
        tools_menu.addAction(backup_manager_action)

        tag_manager_action = QAction("Manage Tags...", self)
        tag_manager_action.triggered.connect(self._open_tag_manager)
        tools_menu.addAction(tag_manager_action)

        tools_menu.addSeparator()

        audit_action = QAction("Security Audit...", self)
        audit_action.triggered.connect(self._run_security_audit)
        tools_menu.addAction(audit_action)

        tools_menu.addSeparator()

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._open_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About pwick", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def _setup_shortcuts(self):
        copy_shortcut = QShortcut(QKeySequence(QKeySequence.StandardKey.Copy), self)
        copy_shortcut.activated.connect(self._copy_password)

        new_password_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.New), self
        )
        new_password_shortcut.activated.connect(self._add_password_entry)

        new_note_shortcut = QShortcut(
            QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_N), self
        )
        new_note_shortcut.activated.connect(self._add_note_entry)

        edit_password_shortcut = QShortcut(
            QKeySequence(QKeyCombination(Qt.ControlModifier, Qt.Key_E)), self
        )
        edit_password_shortcut.activated.connect(self._edit_password_entry)

        save_note_shortcut = QShortcut(
            QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_E), self
        )
        save_note_shortcut.activated.connect(self._save_note_entry)

        delete_password_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Delete), self
        )
        delete_password_shortcut.activated.connect(self._delete_password_entry)

        delete_note_shortcut = QShortcut(
            QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Delete), self
        )
        delete_note_shortcut.activated.connect(self._delete_note_entry)

        lock_shortcut = QShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_L), self)
        lock_shortcut.activated.connect(self._lock_vault)

        # Command Palette (Ctrl+K)
        command_palette_shortcut = QShortcut(
            QKeySequence(Qt.ControlModifier | Qt.Key_K), self
        )
        command_palette_shortcut.activated.connect(self._show_command_palette)

        focus_shortcut = QShortcut(QKeySequence(QKeySequence.StandardKey.Find), self)
        focus_shortcut.activated.connect(
            lambda: (
                self.search_passwords.setFocus()
                if self.tabs.currentIndex() == 0
                else self.search_notes.setFocus()
            )
        )

    def _clear_clipboard(self):
        try:
            pyperclip.copy("")
            self.statusBar().showMessage("Clipboard cleared for security", 2000)
        except Exception as e:
            logger.warning(f"Failed to clear clipboard: {e}")
            # Silently fail for clipboard clear - not critical

    def _add_to_clipboard_history(self, title: str, text: str):
        """
        Add an item to the clipboard history.

        Security Note: Passwords are stored in-memory in plaintext for clipboard history.
        This is necessary for the reuse functionality. History is cleared on lock/quit
        and refreshes daily. This is a known trade-off between usability and security.
        """
        today = date.today()
        if today != self.clipboard_history_date:
            self.clipboard_history.clear()
            self.clipboard_history_date = today

        now = datetime.now()
        entry = {
            "title": title,
            "text": text,  # Store full password for reuse
            "display_text": text[:50] + "..." if len(text) > 50 else text,
            "timestamp": now.strftime("%H:%M:%S"),
        }

        self.clipboard_history.insert(0, entry)

        if len(self.clipboard_history) > self.max_clipboard_history:
            self.clipboard_history = self.clipboard_history[
                : self.max_clipboard_history
            ]

        self._refresh_clipboard_history()

    def _refresh_clipboard_history(self):
        self.clipboard_history_list.clear()
        for entry in self.clipboard_history:
            display_text = (
                f"[{entry['timestamp']}] {entry['title']}: {entry['display_text']}"
            )
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, entry["text"])  # Store full password for copying
            self.clipboard_history_list.addItem(item)

    def _on_clipboard_history_double_click(self, item):
        password_text = item.data(Qt.UserRole)
        if password_text:
            # Encrypt before copying to clipboard (with error handling)
            if self._safe_clipboard_copy(password_text, encrypted=True):
                timeout_ms = self.settings["clipboard_clear_seconds"] * 1000
                self.clipboard_timer.start(timeout_ms)
                self.statusBar().showMessage(
                    f"Copied from history (encrypted)! Will auto-clear in {self.settings['clipboard_clear_seconds']}s",
                    2000,
                )

    def _show_welcome(self):
        dialog = WelcomeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            action = dialog.result_action
            path = dialog.vault_path

            if action == "create":
                self._create_vault(path)
            elif action == "import":
                self._import_vault(path)
            elif action == "open":
                self._open_vault(path)
        else:
            sys.exit(0)

    def _create_vault(self, path: str):
        logger.info(f"Creating new vault at: {path}")
        password_dialog = MasterPasswordDialog(confirm_mode=True, parent=self)
        if password_dialog.exec() == QDialog.Accepted:
            try:
                self.vault_data = vault.create_vault(path, password_dialog.password)
                vault.ensure_vault_compatibility(self.vault_data)
                self.vault_path = path
                self.master_password = password_dialog.password
                self._refresh_lists()
                logger.info("Vault created successfully")
                QMessageBox.information(self, "Success", "Vault created successfully!")
            except Exception as e:
                logger.error(f"Failed to create vault: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to create vault: {e}")
                self._show_welcome()
        else:
            logger.info("Vault creation cancelled by user")
            self._show_welcome()

    def _import_vault(self, source_path: str):
        logger.info(f"Importing vault from: {source_path}")
        password_dialog = MasterPasswordDialog(parent=self)
        if password_dialog.exec() == QDialog.Accepted:
            target_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Imported Vault As",
                "",
                "Vault Files (*.vault);;All Files (*)",
            )
            if target_path:
                if not target_path.endswith(".vault"):
                    target_path += ".vault"
                try:
                    self.vault_data = vault.import_encrypted(
                        source_path, target_path, password_dialog.password
                    )
                    vault.ensure_vault_compatibility(self.vault_data)
                    self.vault_path = target_path
                    self.master_password = password_dialog.password
                    self._refresh_lists()
                    logger.info(f"Vault imported successfully to: {target_path}")
                    QMessageBox.information(
                        self, "Success", "Vault imported successfully!"
                    )
                except vault.VaultAuthenticationError:
                    logger.warning("Vault import failed: Incorrect master password")
                    QMessageBox.critical(self, "Error", "Incorrect master password.")
                    self._show_welcome()
                except Exception as e:
                    logger.error(f"Failed to import vault: {e}", exc_info=True)
                    QMessageBox.critical(self, "Error", f"Failed to import vault: {e}")
                    self._show_welcome()
            else:
                logger.info("Vault import cancelled by user")
                self._show_welcome()
        else:
            logger.info("Vault import cancelled by user")
            self._show_welcome()

    def _open_vault(self, path: str):
        logger.info(f"Opening vault at: {path}")
        password_dialog = MasterPasswordDialog(parent=self)
        if password_dialog.exec() == QDialog.Accepted:
            try:
                self.vault_data = vault.load_vault(path, password_dialog.password)
                vault.ensure_vault_compatibility(self.vault_data)
                self.vault_path = path
                self.master_password = password_dialog.password
                self._refresh_lists()
                logger.info(
                    f"Vault opened successfully with {len(self.vault_data['entries'])} entries"
                )
            except vault.VaultAuthenticationError:
                logger.warning("Vault open failed: Incorrect master password")
                QMessageBox.critical(self, "Error", "Incorrect master password.")
                self._show_welcome()
            except vault.VaultIntegrityError as e:
                logger.error(f"Vault integrity check failed: {e}")
                QMessageBox.critical(
                    self,
                    "Integrity Error",
                    "Vault integrity check failed. The file may be corrupted or tampered with.\n\n"
                    "Do NOT use this vault. Restore from a backup if available.",
                )
                self._show_welcome()
            except Exception as e:
                logger.error(f"Failed to open vault: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to open vault: {e}")
                self._show_welcome()
        else:
            logger.info("Vault open cancelled by user")
            self._show_welcome()

    def _get_sort_key(self, entry: dict):
        """Get sort key based on current sort mode."""
        sort_mode = self.sort_combo.currentIndex() if hasattr(self, "sort_combo") else 0

        # Always put pinned entries first
        pinned_priority = not entry.get("pinned", False)

        if sort_mode == 0:  # Alphabetical (A-Z)
            return (pinned_priority, entry["title"].lower())
        elif sort_mode == 1:  # Alphabetical (Z-A)
            return (pinned_priority, entry["title"].lower()), True  # Reverse flag
        elif sort_mode == 2:  # Date Created (Newest)
            return (pinned_priority, entry.get("created_at", "")), True
        elif sort_mode == 3:  # Date Created (Oldest)
            return (pinned_priority, entry.get("created_at", ""))
        elif sort_mode == 4:  # Date Modified (Newest)
            return (pinned_priority, entry.get("updated_at", "")), True
        elif sort_mode == 5:  # Date Modified (Oldest)
            return (pinned_priority, entry.get("updated_at", ""))
        else:
            return (pinned_priority, entry["title"].lower())

    def _refresh_lists(self):
        self.entry_list.clear()
        self.note_list.clear()
        if self.vault_data:
            # Get sort mode and determine if reverse is needed
            sort_mode = (
                self.sort_combo.currentIndex() if hasattr(self, "sort_combo") else 0
            )
            reverse = sort_mode in [1, 2, 4]  # Z-A, Newest Created, Newest Modified

            # Sort entries based on selected mode
            entries = sorted(
                self.vault_data["entries"],
                key=lambda e: (
                    not e.get("pinned", False),
                    (
                        e["title"].lower()
                        if sort_mode <= 1
                        else e.get("created_at" if sort_mode <= 3 else "updated_at", "")
                    ),
                ),
                reverse=reverse,
            )

            for entry in entries:
                # Build display text with pin indicator and tags
                display_text = entry["title"]

                # Add pin indicator
                if entry.get("pinned", False):
                    display_text = f"📌 {display_text}"

                # Add tags (if any)
                tags = entry.get("tags", [])
                if tags:
                    tag_text = ", ".join(tags)
                    display_text = f"{display_text} [{tag_text}]"

                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, entry["id"])

                if entry.get("type", "password") == "password":
                    self.entry_list.addItem(item)
                elif entry.get("type") == "note":
                    self.note_list.addItem(item)

        # Populate tag filter with current tags
        self._populate_tag_filter()

        self._filter_lists()

    def _filter_lists(self):
        # Get filter mode
        filter_mode = (
            self.filter_combo.currentIndex() if hasattr(self, "filter_combo") else 0
        )
        # 0 = All Entries, 1 = Pinned Only, 2 = Unpinned Only

        # Get tag filter
        selected_tag = None
        if hasattr(self, "tag_filter_combo"):
            tag_text = self.tag_filter_combo.currentText()
            if tag_text != "All Tags":
                selected_tag = tag_text

        # Filter passwords
        password_filter = self.search_passwords.text().lower()
        for i in range(self.entry_list.count()):
            item = self.entry_list.item(i)
            entry_id = item.data(Qt.UserRole)
            entry = self._find_entry(entry_id)

            # Check text filter
            text_match = password_filter in item.text().lower()

            # Check pinned filter
            pinned_match = True
            if entry and filter_mode == 1:  # Pinned Only
                pinned_match = entry.get("pinned", False)
            elif entry and filter_mode == 2:  # Unpinned Only
                pinned_match = not entry.get("pinned", False)

            # Check tag filter
            tag_match = True
            if entry and selected_tag:
                entry_tags = entry.get("tags", [])
                tag_match = selected_tag in entry_tags

            item.setHidden(not (text_match and pinned_match and tag_match))

        # Filter notes
        note_filter = self.search_notes.text().lower()
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            item.setHidden(note_filter not in item.text().lower())

    def _import_csv(self):
        if not self.vault_data:
            QMessageBox.warning(self, "Warning", "Please open or create a vault first.")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                imported_count = 0
                for row in reader:
                    title = row.get("title", "").strip() or row.get("name", "").strip()
                    username = row.get("username", "").strip()
                    password = row.get("password", "").strip()
                    notes = row.get("notes", "").strip() or row.get("note", "").strip()

                    additional_notes = [
                        f"{k}: {v.strip()}"
                        for k, v in row.items()
                        if k
                        not in [
                            "title",
                            "name",
                            "username",
                            "password",
                            "notes",
                            "note",
                        ]
                        and v.strip()
                    ]
                    if additional_notes:
                        notes = (
                            f"{notes}\n\n" + "\n".join(additional_notes)
                            if notes
                            else "\n".join(additional_notes)
                        )

                    if not title:
                        QMessageBox.warning(
                            self, "Warning", f"Skipping row due to missing title: {row}"
                        )
                        continue

                    vault.add_entry(self.vault_data, title, username, password, notes)
                    imported_count += 1
                self._save_vault()
                self._refresh_lists()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully imported {imported_count} entries from CSV.",
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import CSV: {e}")

    def _on_entry_selected(self, current, previous):
        if not current:
            self._clear_details()
            return

        entry_id = current.data(Qt.UserRole)
        self.current_entry_id = entry_id
        entry = self._find_entry(entry_id)

        if not entry:
            self._clear_details()
            return

        if entry.get("type", "password") == "password":
            self.detail_title.setText(entry["title"])
            self.detail_username.setText(entry.get("username", "-"))
            self.detail_password.setText("••••••••")
            self.detail_notes.setText(entry.get("notes", "-"))
        elif entry.get("type") == "note":
            self.note_detail_title.setText(entry["title"])
            self.note_detail_content.setText(entry.get("notes", ""))

    def _clear_details(self):
        self.current_entry_id = None
        # Password tab
        self.detail_title.setText("-")
        self.detail_username.setText("-")
        self.detail_password.setText("••••••••")
        self.detail_notes.setText("-")
        # Note tab
        self.note_detail_title.clear()
        self.note_detail_content.clear()

    def _find_entry(self, entry_id: str) -> Optional[vault.Entry]:
        if self.vault_data:
            for entry in self.vault_data["entries"]:
                if entry["id"] == entry_id:
                    return entry
        return None

    def _get_all_tags(self) -> list[str]:
        """Collect all unique tags from vault entries for autocomplete."""
        if not self.vault_data:
            return []

        all_tags = set()
        for entry in self.vault_data["entries"]:
            tags = entry.get("tags", [])
            if tags:
                all_tags.update(tags)

        return sorted(list(all_tags))

    def _populate_tag_filter(self):
        """Populate the tag filter dropdown with all available tags."""
        if not hasattr(self, "tag_filter_combo"):
            return

        # Save current selection
        current_tag = self.tag_filter_combo.currentText()

        # Clear and repopulate
        self.tag_filter_combo.clear()
        self.tag_filter_combo.addItem("All Tags")

        all_tags = self._get_all_tags()
        for tag in all_tags:
            self.tag_filter_combo.addItem(tag)

        # Restore selection if it still exists
        index = self.tag_filter_combo.findText(current_tag)
        if index >= 0:
            self.tag_filter_combo.setCurrentIndex(index)

    def _add_password_entry(self):
        all_tags = self._get_all_tags()
        dialog = EntryDialog(settings=self.settings, all_tags=all_tags, parent=self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.result_data
            vault.add_entry(
                self.vault_data,
                data["title"],
                data["username"],
                data["password"],
                data["notes"],
                entry_type="password",
                tags=data.get("tags", []),
                pinned=data.get("pinned", False),
            )
            self._save_vault()
            self._refresh_lists()

    def _edit_password_entry(self):
        if not self.current_entry_id:
            QMessageBox.warning(
                self, "Warning", "Please select a password entry to edit."
            )
            return

        entry = self._find_entry(self.current_entry_id)
        if entry and entry.get("type", "password") == "password":
            all_tags = self._get_all_tags()
            dialog = EntryDialog(
                entry_data=entry, settings=self.settings, all_tags=all_tags, parent=self
            )
            if dialog.exec() == QDialog.Accepted:
                data = dialog.result_data
                vault.update_entry(self.vault_data, self.current_entry_id, **data)
                self._save_vault()
                self._refresh_lists()
                for i in range(self.entry_list.count()):
                    item = self.entry_list.item(i)
                    if item.data(Qt.UserRole) == self.current_entry_id:
                        self.entry_list.setCurrentItem(item)
                        break

    def _delete_password_entry(self):
        if not self.current_entry_id:
            QMessageBox.warning(
                self, "Warning", "Please select a password entry to delete."
            )
            return

        entry = self._find_entry(self.current_entry_id)
        if entry and entry.get("type", "password") == "password":
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this password entry?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                vault.delete_entry(self.vault_data, self.current_entry_id)
                self._save_vault()
                self._refresh_lists()
                self._clear_details()

    def _add_note_entry(self):
        if not self.vault_data:
            QMessageBox.warning(self, "Warning", "Please open or create a vault first.")
            return

        title, ok = QInputDialog.getText(self, "Add Note", "Note Title:")
        if ok and title:
            note_id = vault.add_note(self.vault_data, title.strip(), "")
            self._save_vault()
            self._refresh_lists()
            for i in range(self.note_list.count()):
                item = self.note_list.item(i)
                if item.data(Qt.UserRole) == note_id:
                    self.note_list.setCurrentItem(item)
                    break

    def _save_note_entry(self):
        if not self.current_entry_id:
            QMessageBox.warning(
                self, "Warning", "Please select a note or add a new one."
            )
            return

        entry = self._find_entry(self.current_entry_id)
        if entry and entry.get("type") == "note":
            title = self.note_detail_title.text().strip()
            content = self.note_detail_content.toPlainText().strip()

            if not title:
                QMessageBox.warning(self, "Error", "Note title cannot be empty.")
                return

            vault.update_note(self.vault_data, self.current_entry_id, title, content)
            self._save_vault()
            self._refresh_lists()
            QMessageBox.information(self, "Success", "Note saved successfully!")

    def _delete_note_entry(self):
        if not self.current_entry_id:
            QMessageBox.warning(self, "Warning", "Please select a note to delete.")
            return

        entry = self._find_entry(self.current_entry_id)
        if entry and entry.get("type") == "note":
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this note entry?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                vault.delete_entry(self.vault_data, self.current_entry_id)
                self._save_vault()
                self._refresh_lists()
                self._clear_details()

    def _copy_password(self):
        if not self.current_entry_id:
            QMessageBox.warning(
                self, "Warning", "Please select an entry to copy password."
            )
            return

        entry = self._find_entry(self.current_entry_id)
        if entry and entry.get("type", "password") == "password":
            password_text = entry["password"]
            # Use safe clipboard copy with error handling
            if self._safe_clipboard_copy(password_text, encrypted=True):
                self._add_to_clipboard_history(entry["title"], password_text)
                timeout_ms = self.settings["clipboard_clear_seconds"] * 1000
                self.clipboard_timer.start(timeout_ms)
                clear_time = self.settings["clipboard_clear_seconds"]
                self.statusBar().showMessage(
                    f"Password copied to clipboard (encrypted)! Will auto-clear in {clear_time}s",
                    3000,
                )

    def _export_vault(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Vault", "", "Encrypted Files (*.encrypted);;All Files (*)"
        )
        if path:
            if not path.endswith(".encrypted"):
                path += ".encrypted"
            try:
                vault.export_encrypted(self.vault_path, path, self.master_password)
                QMessageBox.information(self, "Success", "Vault exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export vault: {e}")

    def _lock_vault(self):
        logger.info("Locking vault")
        self.vault_data = None
        self.vault_path = None
        self.master_password = None
        self.current_entry_id = None
        self.clipboard_history.clear()  # Clear clipboard history for security
        self.entry_list.clear()
        self.note_list.clear()
        self.auto_lock_timer.stop()
        self._show_welcome()
        logger.info("Vault locked successfully")

    def _open_tag_manager(self):
        """Open the tag manager dialog."""
        if not self.vault_data:
            QMessageBox.warning(
                self, "No Vault", "Please open or create a vault first."
            )
            return

        dialog = TagManagerDialog(self.vault_data, self)
        dialog.exec()

        # If tags were modified, save vault and refresh lists
        if dialog.modified:
            self._save_vault()
            self._refresh_lists()

    def _open_settings_dialog(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Reload settings
            self.settings = load_settings()
            self.auto_lock_minutes = self.settings["auto_lock_minutes"]
            self.max_clipboard_history = self.settings["clipboard_history_size"]

            # Restart auto-lock timer with new timeout
            if self.vault_data and self.auto_lock_minutes > 0:
                self.auto_lock_timer.start(self.auto_lock_minutes * 60 * 1000)
            else:
                self.auto_lock_timer.stop()

    def _run_security_audit(self):
        """Run security audit on vault."""
        if not self.vault_data:
            QMessageBox.warning(
                self, "No Vault", "Please open or create a vault first."
            )
            return

        dialog = SecurityAuditDialog(self.vault_data, self)
        dialog.exec()

    def _open_backup_manager(self):
        """Open the backup manager dialog."""
        if not self.vault_path:
            QMessageBox.warning(
                self, "No Vault", "Please open or create a vault first."
            )
            return

        dialog = BackupManagerDialog(self.vault_path, self.settings, self)
        result = dialog.exec()

        # If vault was restored, we should reload it
        if result == QDialog.Accepted:
            # Prompt user to reload vault
            reply = QMessageBox.question(
                self,
                "Reload Vault?",
                "Would you like to reload the vault to see the restored data?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self._lock_vault()

    def _open_import_wizard(self):
        """Open the import wizard dialog."""
        if not self.vault_data or not self.vault_path:
            QMessageBox.warning(
                self, "No Vault", "Please open or create a vault first."
            )
            return

        dialog = ImportWizardDialog(self.vault_data, self)
        result = dialog.exec()

        # If import succeeded, save vault and refresh lists
        if result == QDialog.Accepted:
            vault.save_vault(self.vault_path, self.vault_data, self.master_password)
            self._refresh_lists()
            QMessageBox.information(
                self,
                "Import Complete",
                "Passwords imported successfully! Vault has been saved.",
            )

    def _show_command_palette(self):
        """Show the command palette."""
        if self.command_palette:
            self.command_palette.exec()

    def _open_settings(self):
        """Open settings dialog (alias for _open_settings_dialog)."""
        self._open_settings_dialog()

    def _show_password_history(self):
        """Show password history for selected entry."""
        if not self.current_entry_id:
            QMessageBox.warning(self, "No Selection", "Please select a password entry.")
            return

        entry = self._find_entry(self.current_entry_id)
        if entry and entry.get("type", "password") == "password":
            dialog = PasswordHistoryDialog(entry, self.encrypted_clipboard, self)
            dialog.exec()

    def _export_csv(self):
        """Export vault entries to CSV file."""
        if not self.vault_data:
            QMessageBox.warning(
                self, "No Vault", "Please open or create a vault first."
            )
            return

        # Warning dialog
        reply = QMessageBox.warning(
            self,
            "Security Warning",
            "⚠️ WARNING: Exporting to CSV will save your passwords in PLAINTEXT.\n\n"
            "This file will NOT be encrypted and anyone who can read it will see your passwords.\n\n"
            "Only export if you understand the security risks and need to transfer data.\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        if not file_path.endswith(".csv"):
            file_path += ".csv"

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["title", "username", "password", "notes", "type"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for entry in self.vault_data["entries"]:
                    writer.writerow(
                        {
                            "title": entry.get("title", ""),
                            "username": entry.get("username", ""),
                            "password": entry.get("password", ""),
                            "notes": entry.get("notes", ""),
                            "type": entry.get("type", "password"),
                        }
                    )

            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {len(self.vault_data['entries'])} entries to {file_path}\n\n"
                "Remember: This file contains PLAINTEXT passwords. Store it securely!",
            )

        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export CSV: {e}")

    def _show_about(self):
        """Show about dialog."""
        from ... import __version__

        QMessageBox.about(
            self,
            "About pwick",
            f"<h2>pwick v{__version__}</h2>"
            "<p>A simple, secure, and 100% local password manager.</p>"
            "<p>Created by orpheus497</p>"
            "<p><b>Your data never leaves your computer.</b></p>"
            "<p>Licensed under the MIT License</p>"
            "<p><a href='https://github.com/orpheus497/pwick'>github.com/orpheus497/pwick</a></p>",
        )

    def _show_shortcuts(self):
        """Show keyboard shortcuts reference."""
        shortcuts_text = """
<h3>Keyboard Shortcuts</h3>
<table>
<tr><td><b>Ctrl+N</b></td><td>Add new password</td></tr>
<tr><td><b>Ctrl+Shift+N</b></td><td>Add new note</td></tr>
<tr><td><b>Ctrl+E</b></td><td>Edit selected password</td></tr>
<tr><td><b>Ctrl+Shift+E</b></td><td>Save selected note</td></tr>
<tr><td><b>Ctrl+C</b></td><td>Copy password</td></tr>
<tr><td><b>Delete</b></td><td>Delete selected password</td></tr>
<tr><td><b>Ctrl+Shift+Delete</b></td><td>Delete selected note</td></tr>
<tr><td><b>Ctrl+F</b></td><td>Focus search box</td></tr>
<tr><td><b>Ctrl+L</b></td><td>Lock vault</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Quit application</td></tr>
</table>
        """

        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)

    def _save_vault(self):
        try:
            vault.save_vault(self.vault_path, self.vault_data, self.master_password)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save vault: {e}")


def run():
    """Run the application."""
    # Load settings to get theme and logging preferences
    settings = load_settings()

    # Setup logging system
    log_level = settings.get("log_level", "INFO")
    log_max_size = (
        settings.get("log_max_size_mb", 10) * 1024 * 1024
    )  # Convert MB to bytes
    setup_logging(level=log_level, max_bytes=log_max_size)

    logger.info("Starting pwick application")

    # Create application
    app = QApplication(sys.argv)

    # Apply theme from settings (with auto-detection support)
    theme_setting = settings.get("theme", "dark")
    if theme_setting == "auto":
        # Auto-detect system theme
        theme = get_auto_theme()
        logger.info(f"Auto-detected system theme: {theme}")
    else:
        theme = theme_setting
    stylesheet = get_stylesheet(theme)
    app.setStyleSheet(stylesheet)
    logger.info(f"Applied {theme} theme")

    # Create and show main window
    window = MainWindow()
    window.show()
    logger.info("Main window displayed")

    # Run application
    exit_code = app.exec()
    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)
