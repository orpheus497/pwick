"""
Backup Manager Dialog for pwick.

Provides a visual interface for managing vault backups, including:
- Browsing available backups
- Previewing backup metadata
- Restoring from backups
- Creating manual backups
- Deleting old backups
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QGroupBox,
    QFormLayout,
)
from PySide6.QtCore import Qt

from ...backup import (
    list_backups,
    create_backup,
    cleanup_old_backups,
    restore_backup,
    get_backup_size,
)


class BackupManagerDialog(QDialog):
    """
    Dialog for managing vault backups.

    Provides a comprehensive interface for backup operations including
    listing, creating, restoring, and cleaning up backups.
    """

    def __init__(self, vault_path: str, settings: dict, parent=None):
        """
        Initialize the Backup Manager dialog.

        Args:
            vault_path: Path to the current vault file
            settings: User settings dictionary
            parent: Parent widget
        """
        super().__init__(parent)
        self.vault_path = vault_path
        self.settings = settings
        self.backups = []

        self.setWindowTitle("Backup Manager")
        self.setModal(True)
        self.resize(700, 500)

        self._setup_ui()
        self._refresh_backup_list()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout()

        # Header
        header = QLabel(
            f"<h2>Backup Manager</h2>"
            f"<p>Manage backups for: <b>{Path(self.vault_path).name}</b></p>"
        )
        layout.addWidget(header)

        # Backup list group
        list_group = QGroupBox("Available Backups")
        list_layout = QVBoxLayout()

        info_label = QLabel(
            "Your vault is automatically backed up based on your settings.\n"
            "You can also create manual backups or restore from any backup below."
        )
        info_label.setWordWrap(True)
        list_layout.addWidget(info_label)

        self.backup_list = QListWidget()
        self.backup_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.backup_list.itemDoubleClicked.connect(self._on_backup_double_clicked)
        list_layout.addWidget(self.backup_list)

        hint_label = QLabel("💡 Tip: Double-click a backup to restore it")
        hint_label.setStyleSheet("color: #999; font-size: 10px; font-style: italic;")
        list_layout.addWidget(hint_label)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Backup details group
        details_group = QGroupBox("Backup Details")
        details_layout = QFormLayout()

        self.detail_filename = QLabel("No backup selected")
        self.detail_date = QLabel("-")
        self.detail_size = QLabel("-")
        self.detail_location = QLabel("-")

        details_layout.addRow("Filename:", self.detail_filename)
        details_layout.addRow("Created:", self.detail_date)
        details_layout.addRow("Size:", self.detail_size)
        details_layout.addRow("Location:", self.detail_location)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.create_backup_btn = QPushButton("Create Backup Now")
        self.create_backup_btn.clicked.connect(self._create_backup)
        button_layout.addWidget(self.create_backup_btn)

        self.restore_btn = QPushButton("Restore Selected")
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self._restore_backup)
        button_layout.addWidget(self.restore_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_backup)
        button_layout.addWidget(self.delete_btn)

        self.cleanup_btn = QPushButton("Cleanup Old Backups")
        self.cleanup_btn.clicked.connect(self._cleanup_backups)
        button_layout.addWidget(self.cleanup_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("primaryButton")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _refresh_backup_list(self):
        """Refresh the list of available backups."""
        self.backup_list.clear()

        backup_location = self.settings.get("auto_backup_location", "")
        backup_dir = backup_location if backup_location else None

        self.backups = list_backups(self.vault_path, backup_dir)

        if not self.backups:
            item = QListWidgetItem("No backups found")
            item.setFlags(Qt.NoItemFlags)
            self.backup_list.addItem(item)
            return

        for backup_path, backup_date in self.backups:
            # Format the display text
            date_str = backup_date.strftime("%Y-%m-%d %H:%M:%S")
            filename = Path(backup_path).name

            # Get file size
            try:
                size_bytes = Path(backup_path).stat().st_size
                size_kb = size_bytes / 1024
                if size_kb < 1024:
                    size_str = f"{size_kb:.1f} KB"
                else:
                    size_str = f"{size_kb / 1024:.1f} MB"
            except (OSError, FileNotFoundError):
                size_str = "Unknown"

            display_text = f"{date_str} - {filename} ({size_str})"

            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, backup_path)
            self.backup_list.addItem(item)

        # Update total size display
        total_size = get_backup_size(self.vault_path, backup_dir)
        if total_size > 0:
            size_mb = total_size / (1024 * 1024)
            self.backup_list.addItem(
                QListWidgetItem(
                    f"\n📊 Total backup size: {size_mb:.2f} MB ({len(self.backups)} backups)"
                )
            )

    def _on_selection_changed(self):
        """Handle backup selection change."""
        current_item = self.backup_list.currentItem()

        if current_item and current_item.data(Qt.UserRole):
            backup_path = current_item.data(Qt.UserRole)
            self.restore_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)

            # Update details
            path_obj = Path(backup_path)
            self.detail_filename.setText(path_obj.name)

            try:
                mtime = datetime.fromtimestamp(path_obj.stat().st_mtime)
                self.detail_date.setText(mtime.strftime("%Y-%m-%d %H:%M:%S"))

                size_bytes = path_obj.stat().st_size
                size_kb = size_bytes / 1024
                if size_kb < 1024:
                    self.detail_size.setText(f"{size_kb:.1f} KB")
                else:
                    self.detail_size.setText(f"{size_kb / 1024:.1f} MB")

                self.detail_location.setText(str(path_obj.parent))
            except Exception as e:
                self.detail_date.setText("Error reading file")
                self.detail_size.setText("-")
                self.detail_location.setText(str(e))
        else:
            self.restore_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.detail_filename.setText("No backup selected")
            self.detail_date.setText("-")
            self.detail_size.setText("-")
            self.detail_location.setText("-")

    def _on_backup_double_clicked(self, item):
        """Handle double-click on backup item."""
        if item.data(Qt.UserRole):
            self._restore_backup()

    def _create_backup(self):
        """Create a new manual backup."""
        backup_location = self.settings.get("auto_backup_location", "")
        backup_dir = backup_location if backup_location else None

        reply = QMessageBox.question(
            self,
            "Create Backup",
            f"Create a backup of the current vault?\n\n"
            f"Vault: {Path(self.vault_path).name}\n"
            f"Location: {backup_dir if backup_dir else 'Same directory as vault'}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            backup_path = create_backup(self.vault_path, backup_dir)

            if backup_path:
                QMessageBox.information(
                    self,
                    "Backup Created",
                    f"Backup created successfully:\n\n{backup_path}",
                )
                self._refresh_backup_list()
            else:
                QMessageBox.critical(
                    self,
                    "Backup Failed",
                    "Failed to create backup. Check the logs for details.",
                )

    def _restore_backup(self):
        """Restore from the selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item or not current_item.data(Qt.UserRole):
            return

        backup_path = current_item.data(Qt.UserRole)

        reply = QMessageBox.warning(
            self,
            "Restore Backup",
            "⚠️ WARNING: Restoring from a backup will REPLACE your current vault file.\n\n"
            "Your current vault will be lost unless you create a backup first.\n\n"
            f"Restore from: {Path(backup_path).name}\n"
            f"Created: {self.detail_date.text()}\n\n"
            "Do you want to create a backup of the current vault before restoring?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Cancel:
            return

        # Create backup of current vault if requested
        if reply == QMessageBox.Yes:
            current_backup = create_backup(self.vault_path)
            if not current_backup:
                QMessageBox.critical(
                    self,
                    "Backup Failed",
                    "Failed to create backup of current vault. Restore cancelled.",
                )
                return

        # Confirm restoration
        final_confirm = QMessageBox.question(
            self,
            "Final Confirmation",
            f"Ready to restore from backup.\n\n"
            f"This will replace:\n{self.vault_path}\n\n"
            f"With:\n{backup_path}\n\n"
            "Continue with restoration?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if final_confirm == QMessageBox.Yes:
            success = restore_backup(backup_path, self.vault_path)

            if success:
                QMessageBox.information(
                    self,
                    "Restore Complete",
                    "Vault restored successfully!\n\n"
                    "You may need to re-open the vault to see the changes.",
                )
                self.accept()  # Close the dialog
            else:
                QMessageBox.critical(
                    self,
                    "Restore Failed",
                    "Failed to restore from backup. Your original vault is unchanged.",
                )

    def _delete_backup(self):
        """Delete the selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item or not current_item.data(Qt.UserRole):
            return

        backup_path = current_item.data(Qt.UserRole)

        reply = QMessageBox.warning(
            self,
            "Delete Backup",
            f"Are you sure you want to delete this backup?\n\n"
            f"File: {Path(backup_path).name}\n"
            f"Created: {self.detail_date.text()}\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                Path(backup_path).unlink()
                QMessageBox.information(
                    self, "Backup Deleted", "Backup deleted successfully."
                )
                self._refresh_backup_list()
            except Exception as e:
                QMessageBox.critical(
                    self, "Delete Failed", f"Failed to delete backup:\n\n{e}"
                )

    def _cleanup_backups(self):
        """Cleanup old backups based on retention settings."""
        keep_count = self.settings.get("auto_backup_keep_count", 5)
        backup_location = self.settings.get("auto_backup_location", "")
        backup_dir = backup_location if backup_location else None

        current_count = len(self.backups)

        if current_count <= keep_count:
            QMessageBox.information(
                self,
                "No Cleanup Needed",
                f"You have {current_count} backup(s), which is within the retention limit of {keep_count}.\n\n"
                "No cleanup needed.",
            )
            return

        will_delete = current_count - keep_count

        reply = QMessageBox.question(
            self,
            "Cleanup Old Backups",
            f"Current backups: {current_count}\n"
            f"Retention limit: {keep_count}\n"
            f"Will delete: {will_delete} oldest backup(s)\n\n"
            "Continue with cleanup?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            deleted = cleanup_old_backups(self.vault_path, backup_dir, keep_count)

            QMessageBox.information(
                self, "Cleanup Complete", f"Deleted {deleted} old backup(s)."
            )
            self._refresh_backup_list()
