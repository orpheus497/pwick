"""
Settings dialog for pwick.

Provides UI for configuring user preferences including:
- General settings (auto-lock, clipboard)
- Password generator settings
- Security settings (Argon2id parameters)
- Appearance settings
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QMessageBox
)
from PySide6.QtCore import Qt

from ...config import load_settings, save_settings, validate_settings, get_default_settings


class SettingsDialog(QDialog):
    """
    Settings dialog for user preferences.

    Provides tabbed interface for different categories of settings.
    All settings are validated before saving.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)

        # Load current settings
        self.settings = load_settings()
        self.original_settings = self.settings.copy()

        self._setup_ui()
        self._load_settings_to_ui()

    def _setup_ui(self):
        """Setup the dialog UI with tabs."""
        layout = QVBoxLayout()

        # Create tab widget
        self.tabs = QTabWidget()

        # Add tabs
        self.tabs.addTab(self._create_general_tab(), "General")
        self.tabs.addTab(self._create_password_gen_tab(), "Password Generator")
        self.tabs.addTab(self._create_security_tab(), "Security")
        self.tabs.addTab(self._create_appearance_tab(), "Appearance")

        layout.addWidget(self.tabs)

        # Buttons
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _create_general_tab(self) -> QWidget:
        """Create the General settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Auto-lock settings
        autolock_group = QGroupBox("Auto-Lock")
        autolock_layout = QFormLayout()

        self.autolock_spin = QSpinBox()
        self.autolock_spin.setMinimum(0)
        self.autolock_spin.setMaximum(1440)  # 24 hours
        self.autolock_spin.setSuffix(" minutes")
        self.autolock_spin.setSpecialValueText("Disabled")
        autolock_layout.addRow("Lock after idle time:", self.autolock_spin)

        autolock_help = QLabel("Vault will automatically lock after this many minutes of inactivity.\n"
                               "Set to 0 to disable auto-lock.")
        autolock_help.setWordWrap(True)
        autolock_help.setStyleSheet("color: #999; font-size: 10px;")
        autolock_layout.addRow("", autolock_help)

        autolock_group.setLayout(autolock_layout)
        layout.addWidget(autolock_group)

        # Clipboard settings
        clipboard_group = QGroupBox("Clipboard")
        clipboard_layout = QFormLayout()

        self.clipboard_clear_spin = QSpinBox()
        self.clipboard_clear_spin.setMinimum(10)
        self.clipboard_clear_spin.setMaximum(600)  # 10 minutes
        self.clipboard_clear_spin.setSuffix(" seconds")
        clipboard_layout.addRow("Auto-clear after:", self.clipboard_clear_spin)

        self.clipboard_history_spin = QSpinBox()
        self.clipboard_history_spin.setMinimum(0)
        self.clipboard_history_spin.setMaximum(100)
        self.clipboard_history_spin.setSpecialValueText("Disabled")
        clipboard_layout.addRow("History size:", self.clipboard_history_spin)

        clipboard_help = QLabel("Copied passwords will be automatically cleared from the system\n"
                               "clipboard after the specified time. History stores recent copies\n"
                               "in memory (cleared on lock).")
        clipboard_help.setWordWrap(True)
        clipboard_help.setStyleSheet("color: #999; font-size: 10px;")
        clipboard_layout.addRow("", clipboard_help)

        clipboard_group.setLayout(clipboard_layout)
        layout.addWidget(clipboard_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_password_gen_tab(self) -> QWidget:
        """Create the Password Generator settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        gen_group = QGroupBox("Password Generator Defaults")
        gen_layout = QFormLayout()

        # Length
        self.gen_length_spin = QSpinBox()
        self.gen_length_spin.setMinimum(8)
        self.gen_length_spin.setMaximum(128)
        self.gen_length_spin.setSuffix(" characters")
        gen_layout.addRow("Default length:", self.gen_length_spin)

        # Character sets
        gen_layout.addRow("", QLabel("Character sets to include:"))

        self.gen_uppercase_check = QCheckBox("Uppercase letters (A-Z)")
        gen_layout.addRow("", self.gen_uppercase_check)

        self.gen_lowercase_check = QCheckBox("Lowercase letters (a-z)")
        gen_layout.addRow("", self.gen_lowercase_check)

        self.gen_digits_check = QCheckBox("Digits (0-9)")
        gen_layout.addRow("", self.gen_digits_check)

        self.gen_punctuation_check = QCheckBox("Punctuation (!@#$%^&*...)")
        gen_layout.addRow("", self.gen_punctuation_check)

        gen_help = QLabel("These are default settings for the password generator.\n"
                         "At least one character set must be selected.\n"
                         "You can override these when generating individual passwords.")
        gen_help.setWordWrap(True)
        gen_help.setStyleSheet("color: #999; font-size: 10px;")
        gen_layout.addRow("", gen_help)

        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_security_tab(self) -> QWidget:
        """Create the Security settings tab (Argon2id parameters)."""
        widget = QWidget()
        layout = QVBoxLayout()

        warning = QLabel("⚠️ WARNING: These are advanced settings for new vaults.\n"
                        "Changing these will NOT affect existing vaults.\n"
                        "Only modify if you understand Argon2id parameters.")
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #c62828; font-weight: bold; padding: 10px; "
                             "background-color: #3d0000; border: 1px solid #c62828; border-radius: 4px;")
        layout.addWidget(warning)

        argon2_group = QGroupBox("Argon2id Parameters for New Vaults")
        argon2_layout = QFormLayout()

        # Time cost
        self.argon2_time_spin = QSpinBox()
        self.argon2_time_spin.setMinimum(1)
        self.argon2_time_spin.setMaximum(10)
        self.argon2_time_spin.setSuffix(" iterations")
        argon2_layout.addRow("Time cost:", self.argon2_time_spin)

        time_help = QLabel("Number of iterations. Higher = slower but more secure.\n"
                          "Recommended: 3 (OWASP standard)")
        time_help.setStyleSheet("color: #999; font-size: 10px;")
        argon2_layout.addRow("", time_help)

        # Memory cost
        self.argon2_memory_spin = QSpinBox()
        self.argon2_memory_spin.setMinimum(8)  # 8 MB minimum
        self.argon2_memory_spin.setMaximum(1024)  # 1 GB maximum
        self.argon2_memory_spin.setSuffix(" MB")
        argon2_layout.addRow("Memory cost:", self.argon2_memory_spin)

        memory_help = QLabel("Memory required in megabytes. Higher = more resistant to attacks.\n"
                            "Recommended: 64 MB (OWASP standard)")
        memory_help.setStyleSheet("color: #999; font-size: 10px;")
        argon2_layout.addRow("", memory_help)

        # Parallelism
        self.argon2_parallel_spin = QSpinBox()
        self.argon2_parallel_spin.setMinimum(1)
        self.argon2_parallel_spin.setMaximum(16)
        self.argon2_parallel_spin.setSuffix(" threads")
        argon2_layout.addRow("Parallelism:", self.argon2_parallel_spin)

        parallel_help = QLabel("Number of parallel threads.\n"
                              "Recommended: 1 (OWASP standard)")
        parallel_help.setStyleSheet("color: #999; font-size: 10px;")
        argon2_layout.addRow("", parallel_help)

        argon2_group.setLayout(argon2_layout)
        layout.addWidget(argon2_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_appearance_tab(self) -> QWidget:
        """Create the Appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()

        theme_label = QLabel("Dark theme (default)")
        theme_label.setStyleSheet("color: #999;")
        theme_layout.addRow("Current theme:", theme_label)

        theme_help = QLabel("Light theme support is planned for a future release.\n"
                           "Currently, only dark theme is available.")
        theme_help.setWordWrap(True)
        theme_help.setStyleSheet("color: #999; font-size: 10px;")
        theme_layout.addRow("", theme_help)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _load_settings_to_ui(self):
        """Load current settings values into UI controls."""
        # General tab
        self.autolock_spin.setValue(self.settings['auto_lock_minutes'])
        self.clipboard_clear_spin.setValue(self.settings['clipboard_clear_seconds'])
        self.clipboard_history_spin.setValue(self.settings['clipboard_history_size'])

        # Password generator tab
        self.gen_length_spin.setValue(self.settings['password_generator_length'])
        self.gen_uppercase_check.setChecked(self.settings['password_generator_use_uppercase'])
        self.gen_lowercase_check.setChecked(self.settings['password_generator_use_lowercase'])
        self.gen_digits_check.setChecked(self.settings['password_generator_use_digits'])
        self.gen_punctuation_check.setChecked(self.settings['password_generator_use_punctuation'])

        # Security tab
        # Convert memory cost from bytes to MB for display
        memory_mb = self.settings['vault_argon2_memory_cost'] // 1024
        self.argon2_time_spin.setValue(self.settings['vault_argon2_time_cost'])
        self.argon2_memory_spin.setValue(memory_mb)
        self.argon2_parallel_spin.setValue(self.settings['vault_argon2_parallelism'])

    def _collect_settings_from_ui(self) -> dict:
        """Collect settings from UI controls into a dictionary."""
        settings = {}

        # General tab
        settings['auto_lock_minutes'] = self.autolock_spin.value()
        settings['clipboard_clear_seconds'] = self.clipboard_clear_spin.value()
        settings['clipboard_history_size'] = self.clipboard_history_spin.value()

        # Password generator tab
        settings['password_generator_length'] = self.gen_length_spin.value()
        settings['password_generator_use_uppercase'] = self.gen_uppercase_check.isChecked()
        settings['password_generator_use_lowercase'] = self.gen_lowercase_check.isChecked()
        settings['password_generator_use_digits'] = self.gen_digits_check.isChecked()
        settings['password_generator_use_punctuation'] = self.gen_punctuation_check.isChecked()

        # Security tab - convert MB back to bytes
        settings['vault_argon2_time_cost'] = self.argon2_time_spin.value()
        settings['vault_argon2_memory_cost'] = self.argon2_memory_spin.value() * 1024
        settings['vault_argon2_parallelism'] = self.argon2_parallel_spin.value()
        settings['vault_argon2_hash_len'] = self.settings['vault_argon2_hash_len']  # Not exposed in UI

        # Appearance tab
        settings['theme'] = self.settings['theme']  # Not changeable yet

        return settings

    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.settings = get_default_settings()
            self._load_settings_to_ui()

    def _on_save(self):
        """Save settings and close dialog."""
        # Collect settings from UI
        new_settings = self._collect_settings_from_ui()

        # Validate settings
        new_settings = validate_settings(new_settings)

        # Save to file
        if save_settings(new_settings):
            self.settings = new_settings
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved successfully.\n"
                "Some changes may require restarting the application."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save settings. Please check file permissions."
            )

    def get_settings(self) -> dict:
        """
        Get the current settings (after dialog closes).

        Returns:
            Dictionary of settings
        """
        return self.settings
