"""
Import Wizard Dialog for pwick.

Provides a user-friendly wizard for importing passwords from other password managers.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QTextEdit,
    QProgressBar,
)

from ...importers import (
    detect_csv_format,
    import_from_csv,
    import_from_keepass_csv,
    import_from_bitwarden_json,
    import_from_bitwarden_csv,
    import_from_lastpass_csv,
    import_from_onepassword_csv,
)
from ... import vault


class ImportWizardDialog(QDialog):
    """
    Wizard dialog for importing passwords from other password managers.

    Supports:
    - Auto-detection of CSV format
    - KeePass CSV
    - Bitwarden JSON/CSV
    - LastPass CSV
    - 1Password CSV
    - Generic CSV
    """

    def __init__(self, vault_obj: vault.Vault, parent=None):
        """
        Initialize the Import Wizard.

        Args:
            vault_obj: Vault to import into
            parent: Parent widget
        """
        super().__init__(parent)
        self.vault_obj = vault_obj
        self.selected_file = ""

        self.setWindowTitle("Import Wizard")
        self.setModal(True)
        self.resize(600, 400)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the wizard UI."""
        layout = QVBoxLayout()

        # Header
        header = QLabel(
            "<h2>Import Passwords</h2>"
            "<p>Import your passwords from another password manager.</p>"
        )
        layout.addWidget(header)

        # Format selection group
        format_group = QGroupBox("Select Source Format")
        format_layout = QVBoxLayout()

        info_label = QLabel(
            "Choose the format you're importing from. The wizard will attempt to auto-detect\n"
            "the format from the file, but you can manually select if needed."
        )
        info_label.setWordWrap(True)
        format_layout.addWidget(info_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(
            [
                "Auto-detect",
                "KeePass CSV",
                "Bitwarden JSON",
                "Bitwarden CSV",
                "LastPass CSV",
                "1Password CSV",
                "Generic CSV",
            ]
        )
        format_layout.addWidget(self.format_combo)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # File selection group
        file_group = QGroupBox("Select Import File")
        file_layout = QVBoxLayout()

        file_button_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #999;")
        file_button_layout.addWidget(self.file_label)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_button_layout.addWidget(browse_btn)

        file_layout.addLayout(file_button_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Preview/Instructions
        preview_group = QGroupBox("Instructions")
        preview_layout = QVBoxLayout()

        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setMaximumHeight(120)
        self.instructions_text.setPlainText(
            "How to export from your password manager:\n\n"
            "• KeePass: Database → Export → CSV\n"
            "• Bitwarden: Tools → Export Vault → JSON or CSV\n"
            "• LastPass: More Options → Advanced → Export\n"
            "• 1Password: File → Export → CSV\n\n"
            "Select a file to continue."
        )

        preview_layout.addWidget(self.instructions_text)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.import_btn = QPushButton("Import")
        self.import_btn.setObjectName("primaryButton")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._do_import)
        button_layout.addWidget(self.import_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _browse_file(self):
        """Browse for import file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Import File",
            "",
            "All Supported Files (*.csv *.json);;CSV Files (*.csv);;JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            self.selected_file = file_path
            self.file_label.setText(Path(file_path).name)
            self.file_label.setStyleSheet("color: #e0e0e0;")
            self.import_btn.setEnabled(True)

            # Try to auto-detect format
            if self.format_combo.currentText() == "Auto-detect":
                detected_format = detect_csv_format(file_path)
                if detected_format:
                    format_map = {
                        "keepass": "KeePass CSV",
                        "bitwarden": "Bitwarden CSV",
                        "lastpass": "LastPass CSV",
                        "1password": "1Password CSV",
                        "generic": "Generic CSV",
                    }
                    if detected_format in format_map:
                        self.format_combo.setCurrentText(format_map[detected_format])
                        self.instructions_text.setPlainText(
                            f"Auto-detected format: {format_map[detected_format]}\n\n"
                            "Click 'Import' to proceed, or select a different format if this is incorrect."
                        )

    def _do_import(self):
        """Perform the import operation."""
        if not self.selected_file:
            QMessageBox.warning(self, "No File", "Please select a file to import.")
            return

        selected_format = self.format_combo.currentText()

        # Confirm before importing
        reply = QMessageBox.question(
            self,
            "Confirm Import",
            f"Import passwords from:\n{Path(self.selected_file).name}\n\n"
            f"Format: {selected_format}\n\n"
            "Existing passwords will not be affected. New entries will be added.\n\n"
            "Continue with import?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply != QMessageBox.Yes:
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.import_btn.setEnabled(False)

        # Perform import based on format
        try:
            if selected_format == "KeePass CSV":
                result = import_from_keepass_csv(self.vault_obj, self.selected_file)
            elif selected_format == "Bitwarden JSON":
                result = import_from_bitwarden_json(self.vault_obj, self.selected_file)
            elif selected_format == "Bitwarden CSV":
                result = import_from_bitwarden_csv(self.vault_obj, self.selected_file)
            elif selected_format == "LastPass CSV":
                result = import_from_lastpass_csv(self.vault_obj, self.selected_file)
            elif selected_format == "1Password CSV":
                result = import_from_onepassword_csv(self.vault_obj, self.selected_file)
            else:  # Auto-detect or Generic CSV
                result = import_from_csv(self.vault_obj, self.selected_file)

            # Hide progress
            self.progress_bar.setVisible(False)
            self.import_btn.setEnabled(True)

            # Show results
            if result.success_count > 0:
                message = "Import complete!\n\n"
                message += f"Successfully imported: {result.success_count} entries\n"

                if result.error_count > 0:
                    message += f"Failed to import: {result.error_count} entries\n\n"
                    message += "Errors:\n"
                    for row_num, error_msg in result.errors[:5]:  # Show first 5 errors
                        message += f"  Row {row_num}: {error_msg}\n"
                    if len(result.errors) > 5:
                        message += f"  ... and {len(result.errors) - 5} more errors\n"

                QMessageBox.information(self, "Import Complete", message)
                self.accept()  # Close dialog on success
            else:
                error_msg = "Failed to import any entries.\n\n"
                if result.errors:
                    error_msg += "Errors:\n"
                    for row_num, error in result.errors[:10]:
                        error_msg += f"  Row {row_num}: {error}\n"

                QMessageBox.critical(self, "Import Failed", error_msg)

        except Exception as e:
            self.progress_bar.setVisible(False)
            self.import_btn.setEnabled(True)

            QMessageBox.critical(
                self, "Import Error", f"An error occurred during import:\n\n{str(e)}"
            )
