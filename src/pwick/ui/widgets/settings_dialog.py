"""
Settings dialog for pwick.

Provides UI for configuring user preferences including:
- General settings (auto-lock, clipboard)
- Password generator settings
- Password management (history, expiration)
- Backup settings (auto-backup, retention)
- Logging settings (level, file size)
- Security settings (Argon2id parameters)
- Appearance settings (theme)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QMessageBox, QComboBox, QLineEdit, QFileDialog
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
        self.tabs.addTab(self._create_password_mgmt_tab(), "Password Management")
        self.tabs.addTab(self._create_backup_tab(), "Backup")
        self.tabs.addTab(self._create_logging_tab(), "Logging")
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

    def _create_password_mgmt_tab(self) -> QWidget:
        """Create the Password Management settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Password history settings
        history_group = QGroupBox("Password History")
        history_layout = QFormLayout()

        self.password_history_limit_spin = QSpinBox()
        self.password_history_limit_spin.setMinimum(0)
        self.password_history_limit_spin.setMaximum(50)
        self.password_history_limit_spin.setSpecialValueText("Disabled")
        history_layout.addRow("Keep last N passwords:", self.password_history_limit_spin)

        history_help = QLabel("Number of old passwords to keep for each entry.\n"
                             "Set to 0 to disable password history.\n"
                             "Useful for tracking password changes and preventing reuse.")
        history_help.setWordWrap(True)
        history_help.setStyleSheet("color: #999; font-size: 10px;")
        history_layout.addRow("", history_help)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # Password expiration settings
        expiration_group = QGroupBox("Password Expiration")
        expiration_layout = QFormLayout()

        self.password_expiration_days_spin = QSpinBox()
        self.password_expiration_days_spin.setMinimum(0)
        self.password_expiration_days_spin.setMaximum(3650)  # 10 years
        self.password_expiration_days_spin.setSuffix(" days")
        self.password_expiration_days_spin.setSpecialValueText("Never")
        expiration_layout.addRow("Expire passwords after:", self.password_expiration_days_spin)

        self.password_expiration_warning_spin = QSpinBox()
        self.password_expiration_warning_spin.setMinimum(1)
        self.password_expiration_warning_spin.setMaximum(365)
        self.password_expiration_warning_spin.setSuffix(" days")
        expiration_layout.addRow("Warn before expiry:", self.password_expiration_warning_spin)

        expiration_help = QLabel("Passwords older than the expiration period will be flagged.\n"
                                "You'll receive warnings before passwords expire.\n"
                                "Set to 0 to disable password expiration.")
        expiration_help.setWordWrap(True)
        expiration_help.setStyleSheet("color: #999; font-size: 10px;")
        expiration_layout.addRow("", expiration_help)

        expiration_group.setLayout(expiration_layout)
        layout.addWidget(expiration_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_backup_tab(self) -> QWidget:
        """Create the Backup settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Auto-backup settings
        autobackup_group = QGroupBox("Automatic Backup")
        autobackup_layout = QFormLayout()

        self.auto_backup_enabled_check = QCheckBox("Enable automatic backups")
        autobackup_layout.addRow("", self.auto_backup_enabled_check)

        self.auto_backup_frequency_combo = QComboBox()
        self.auto_backup_frequency_combo.addItems(["On every save", "Daily", "Weekly"])
        autobackup_layout.addRow("Backup frequency:", self.auto_backup_frequency_combo)

        self.auto_backup_keep_count_spin = QSpinBox()
        self.auto_backup_keep_count_spin.setMinimum(1)
        self.auto_backup_keep_count_spin.setMaximum(100)
        self.auto_backup_keep_count_spin.setSuffix(" backups")
        autobackup_layout.addRow("Keep most recent:", self.auto_backup_keep_count_spin)

        # Backup location
        location_layout = QHBoxLayout()
        self.auto_backup_location_edit = QLineEdit()
        self.auto_backup_location_edit.setPlaceholderText("Same folder as vault (default)")
        location_layout.addWidget(self.auto_backup_location_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_backup_location)
        location_layout.addWidget(browse_btn)

        autobackup_layout.addRow("Backup location:", location_layout)

        backup_help = QLabel("Automatic backups create timestamped copies of your vault.\n"
                            "Old backups are automatically cleaned up based on retention settings.\n"
                            "Leave location empty to save backups next to the vault file.")
        backup_help.setWordWrap(True)
        backup_help.setStyleSheet("color: #999; font-size: 10px;")
        autobackup_layout.addRow("", backup_help)

        autobackup_group.setLayout(autobackup_layout)
        layout.addWidget(autobackup_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_logging_tab(self) -> QWidget:
        """Create the Logging settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        logging_group = QGroupBox("Application Logging")
        logging_layout = QFormLayout()

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        logging_layout.addRow("Log level:", self.log_level_combo)

        self.log_max_size_spin = QSpinBox()
        self.log_max_size_spin.setMinimum(1)
        self.log_max_size_spin.setMaximum(100)
        self.log_max_size_spin.setSuffix(" MB")
        logging_layout.addRow("Max log file size:", self.log_max_size_spin)

        log_help = QLabel("Logs are stored in the application config directory.\n"
                         "Sensitive data (passwords, master password) is never logged.\n\n"
                         "Log levels:\n"
                         "• DEBUG: Detailed diagnostic information\n"
                         "• INFO: General informational messages (recommended)\n"
                         "• WARNING: Warning messages only\n"
                         "• ERROR: Error messages only\n\n"
                         "Log files rotate automatically when size limit is reached.")
        log_help.setWordWrap(True)
        log_help.setStyleSheet("color: #999; font-size: 10px;")
        logging_layout.addRow("", log_help)

        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)

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

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        theme_layout.addRow("Color theme:", self.theme_combo)

        theme_help = QLabel("Choose between dark and light color themes, or Auto to match system theme.\n"
                           "Changing the theme requires restarting the application.")
        theme_help.setWordWrap(True)
        theme_help.setStyleSheet("color: #999; font-size: 10px;")
        theme_layout.addRow("", theme_help)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _browse_backup_location(self):
        """Open folder browser for backup location."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Location",
            self.auto_backup_location_edit.text() or ""
        )
        if directory:
            self.auto_backup_location_edit.setText(directory)

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

        # Password management tab
        self.password_history_limit_spin.setValue(self.settings.get('password_history_limit', 5))
        self.password_expiration_days_spin.setValue(self.settings.get('password_expiration_days', 90))
        self.password_expiration_warning_spin.setValue(self.settings.get('password_expiration_warning_days', 14))

        # Backup tab
        self.auto_backup_enabled_check.setChecked(self.settings.get('auto_backup_enabled', False))
        frequency_map = {'on_change': 0, 'daily': 1, 'weekly': 2}
        frequency = self.settings.get('auto_backup_frequency', 'weekly')
        self.auto_backup_frequency_combo.setCurrentIndex(frequency_map.get(frequency, 2))
        self.auto_backup_keep_count_spin.setValue(self.settings.get('auto_backup_keep_count', 5))
        self.auto_backup_location_edit.setText(self.settings.get('auto_backup_location', ''))

        # Logging tab
        log_level = self.settings.get('log_level', 'INFO')
        log_level_map = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3}
        self.log_level_combo.setCurrentIndex(log_level_map.get(log_level, 1))
        self.log_max_size_spin.setValue(self.settings.get('log_max_size_mb', 10))

        # Security tab
        # Convert memory cost from bytes to MB for display
        memory_mb = self.settings['vault_argon2_memory_cost'] // 1024
        self.argon2_time_spin.setValue(self.settings['vault_argon2_time_cost'])
        self.argon2_memory_spin.setValue(memory_mb)
        self.argon2_parallel_spin.setValue(self.settings['vault_argon2_parallelism'])

        # Appearance tab
        theme = self.settings.get('theme', 'dark')
        theme_map = {'dark': 0, 'light': 1, 'auto': 2}
        self.theme_combo.setCurrentIndex(theme_map.get(theme, 0))

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

        # Password management tab
        settings['password_history_limit'] = self.password_history_limit_spin.value()
        settings['password_expiration_days'] = self.password_expiration_days_spin.value()
        settings['password_expiration_warning_days'] = self.password_expiration_warning_spin.value()

        # Backup tab
        settings['auto_backup_enabled'] = self.auto_backup_enabled_check.isChecked()
        frequency_values = ['on_change', 'daily', 'weekly']
        settings['auto_backup_frequency'] = frequency_values[self.auto_backup_frequency_combo.currentIndex()]
        settings['auto_backup_keep_count'] = self.auto_backup_keep_count_spin.value()
        settings['auto_backup_location'] = self.auto_backup_location_edit.text().strip()

        # Logging tab
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        settings['log_level'] = log_levels[self.log_level_combo.currentIndex()]
        settings['log_max_size_mb'] = self.log_max_size_spin.value()

        # Security tab - convert MB back to bytes
        settings['vault_argon2_time_cost'] = self.argon2_time_spin.value()
        settings['vault_argon2_memory_cost'] = self.argon2_memory_spin.value() * 1024
        settings['vault_argon2_parallelism'] = self.argon2_parallel_spin.value()
        settings['vault_argon2_hash_len'] = self.settings['vault_argon2_hash_len']  # Not exposed in UI

        # Appearance tab
        theme_values = ['dark', 'light', 'auto']
        settings['theme'] = theme_values[self.theme_combo.currentIndex()]

        # Entry sorting (not exposed in UI yet, preserve existing)
        settings['entry_sort_order'] = self.settings.get('entry_sort_order', 'alphabetical')

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
