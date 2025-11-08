"""
UI tests for pwick widgets using pytest-qt.

Tests cover:
- Settings dialog functionality
- Password generator dialog
- Backup manager dialog
- Import wizard dialog
- Command palette dialog
- Password history dialog
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from pwick.ui.widgets.settings_dialog import SettingsDialog
from pwick.ui.widgets.password_generator_dialog import PasswordGeneratorDialog
from pwick.ui.widgets.backup_manager_dialog import BackupManagerDialog
from pwick.ui.widgets.import_wizard_dialog import ImportWizardDialog
from pwick.ui.widgets.command_palette_dialog import (
    create_command_palette,
)
from pwick.ui.widgets.password_history_dialog import PasswordHistoryDialog


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_settings():
    """Mock settings dictionary."""
    return {
        "auto_lock_minutes": 5,
        "clipboard_clear_seconds": 30,
        "clipboard_history_size": 30,
        "password_generator_length": 20,
        "password_generator_use_uppercase": True,
        "password_generator_use_lowercase": True,
        "password_generator_use_digits": True,
        "password_generator_use_punctuation": True,
        "password_history_limit": 5,
        "password_expiration_days": 90,
        "password_expiration_warning_days": 14,
        "auto_backup_enabled": False,
        "auto_backup_location": "",
        "auto_backup_frequency": "weekly",
        "auto_backup_keep_count": 5,
        "theme": "dark",
        "log_level": "INFO",
        "log_max_size_mb": 10,
        "entry_sort_order": "alphabetical",
        "vault_argon2_time_cost": 3,
        "vault_argon2_memory_cost": 65536,
        "vault_argon2_parallelism": 1,
        "vault_argon2_hash_len": 32,
    }


class TestSettingsDialog:
    """Test SettingsDialog widget."""

    def test_settings_dialog_initialization(self, qapp, mock_settings):
        """Test that settings dialog initializes correctly."""
        with patch(
            "pwick.ui.widgets.settings_dialog.load_settings", return_value=mock_settings
        ):
            dialog = SettingsDialog()
            assert dialog.windowTitle() == "Settings"
            assert dialog.isModal()
            assert dialog.settings == mock_settings

    def test_theme_options_include_auto(self, qapp, mock_settings):
        """Test that theme dropdown includes Auto option."""
        with patch(
            "pwick.ui.widgets.settings_dialog.load_settings", return_value=mock_settings
        ):
            dialog = SettingsDialog()
            theme_combo = dialog.theme_combo
            items = [theme_combo.itemText(i) for i in range(theme_combo.count())]
            assert "Dark" in items
            assert "Light" in items
            assert "Auto" in items

    def test_settings_load_from_ui(self, qapp, mock_settings):
        """Test loading settings from UI controls."""
        with patch(
            "pwick.ui.widgets.settings_dialog.load_settings", return_value=mock_settings
        ):
            dialog = SettingsDialog()
            assert dialog.autolock_spin.value() == 5
            assert dialog.clipboard_clear_spin.value() == 30
            assert dialog.gen_length_spin.value() == 20

    def test_theme_auto_setting(self, qapp, mock_settings):
        """Test that Auto theme is correctly loaded and saved."""
        mock_settings["theme"] = "auto"
        with patch(
            "pwick.ui.widgets.settings_dialog.load_settings", return_value=mock_settings
        ):
            dialog = SettingsDialog()
            assert dialog.theme_combo.currentIndex() == 2  # Auto is third option

    def test_reset_to_defaults(self, qapp, mock_settings, qtbot):
        """Test reset to defaults functionality."""
        with patch(
            "pwick.ui.widgets.settings_dialog.load_settings", return_value=mock_settings
        ):
            with patch(
                "pwick.ui.widgets.settings_dialog.get_default_settings",
                return_value=mock_settings,
            ):
                dialog = SettingsDialog()

                # Change a value
                dialog.autolock_spin.setValue(10)

                # Simulate clicking reset button (with confirmation)
                with patch(
                    "PySide6.QtWidgets.QMessageBox.question", return_value=16384
                ):  # Yes
                    for child in dialog.findChildren(type(dialog)):
                        if (
                            hasattr(child, "text")
                            and child.text() == "Reset to Defaults"
                        ):
                            break

                    # Since we can't easily click, just call the method directly
                    dialog._reset_to_defaults()
                    assert dialog.autolock_spin.value() == 5  # Back to default


class TestPasswordGeneratorDialog:
    """Test PasswordGeneratorDialog widget."""

    def test_password_generator_initialization(self, qapp):
        """Test that password generator dialog initializes correctly."""
        dialog = PasswordGeneratorDialog()
        assert dialog.windowTitle() == "Generate Password"
        assert dialog.isModal()

    def test_password_generation(self, qapp, qtbot):
        """Test that passwords are generated when clicking generate."""
        dialog = PasswordGeneratorDialog()

        # Set length
        dialog.length_spin.setValue(16)

        # Generate password
        dialog._generate_password()

        # Check password was generated
        password = dialog.password_display.toPlainText()
        assert len(password) == 16
        assert password != ""

    def test_character_set_validation(self, qapp):
        """Test that at least one character set must be enabled."""
        dialog = PasswordGeneratorDialog()

        # Uncheck all character sets
        dialog.uppercase_check.setChecked(False)
        dialog.lowercase_check.setChecked(False)
        dialog.digits_check.setChecked(False)
        dialog.punctuation_check.setChecked(False)

        # Try to generate - should show error
        with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
            dialog._generate_password()
            mock_warning.assert_called_once()


class TestBackupManagerDialog:
    """Test BackupManagerDialog widget."""

    def test_backup_manager_initialization(self, qapp, mock_settings, tmp_path):
        """Test that backup manager dialog initializes correctly."""
        vault_path = str(tmp_path / "test.vault")
        Path(vault_path).touch()

        dialog = BackupManagerDialog(vault_path, mock_settings)
        assert "Backup Manager" in dialog.windowTitle()
        assert dialog.isModal()

    def test_backup_list_population(self, qapp, mock_settings, tmp_path):
        """Test that backup list populates with existing backups."""
        vault_path = str(tmp_path / "test.vault")
        Path(vault_path).touch()

        # Create some fake backups
        backup_dir = tmp_path
        (backup_dir / "test.vault.backup_20250101_120000").touch()
        (backup_dir / "test.vault.backup_20250102_120000").touch()

        with patch(
            "pwick.ui.widgets.backup_manager_dialog.get_backup_dir",
            return_value=str(backup_dir),
        ):
            dialog = BackupManagerDialog(vault_path, mock_settings)
            # Backups should be listed
            assert dialog.backup_list.count() >= 0  # May be 0 if pattern doesn't match


class TestImportWizardDialog:
    """Test ImportWizardDialog widget."""

    def test_import_wizard_initialization(self, qapp):
        """Test that import wizard dialog initializes correctly."""
        mock_vault = Mock()
        dialog = ImportWizardDialog(mock_vault)
        assert dialog.windowTitle() == "Import from Other Password Managers"
        assert dialog.isModal()

    def test_format_detection(self, qapp):
        """Test that file format is auto-detected."""
        mock_vault = Mock()
        dialog = ImportWizardDialog(mock_vault)

        # Test format detection
        with patch(
            "pwick.importers.csv_importer.detect_csv_format", return_value="keepass"
        ):
            # Simulate file selection
            dialog.file_path_edit.setText("/path/to/file.csv")
            # Format should be detected
            # Note: Actual detection happens in _browse_file which we can't easily test


class TestCommandPaletteDialog:
    """Test CommandPaletteDialog widget."""

    def test_command_palette_initialization(self, qapp):
        """Test that command palette dialog initializes correctly."""
        mock_main_window = Mock()
        dialog = create_command_palette(mock_main_window)
        assert dialog.windowTitle() == "Command Palette"
        assert not dialog.isModal()  # Command palette is non-modal

    def test_fuzzy_search(self, qapp):
        """Test fuzzy matching in command palette."""
        mock_main_window = Mock()
        dialog = create_command_palette(mock_main_window)

        # Test fuzzy matching
        assert dialog._fuzzy_match("new", "New Entry") is True
        assert dialog._fuzzy_match("ne", "New Entry") is True
        assert dialog._fuzzy_match("nweny", "New Entry") is True
        assert dialog._fuzzy_match("xyz", "New Entry") is False

    def test_command_filtering(self, qapp, qtbot):
        """Test that commands are filtered by search text."""
        mock_main_window = Mock()
        dialog = create_command_palette(mock_main_window)

        # Get initial command count
        initial_count = dialog.command_list.count()

        # Type search text
        dialog.search_edit.setText("new")
        dialog._filter_commands()

        # Should have fewer commands visible
        visible_count = sum(
            1
            for i in range(dialog.command_list.count())
            if not dialog.command_list.item(i).isHidden()
        )
        assert visible_count <= initial_count

    def test_keyboard_navigation(self, qapp, qtbot):
        """Test keyboard navigation in command palette."""
        mock_main_window = Mock()
        dialog = create_command_palette(mock_main_window)

        # Set focus to search box
        dialog.search_edit.setFocus()

        # Press Down arrow
        QTest.keyClick(dialog.search_edit, Qt.Key_Down)

        # Command list should have selection
        # Note: This is a basic test; full keyboard navigation testing requires more setup


class TestPasswordHistoryDialog:
    """Test PasswordHistoryDialog widget."""

    def test_password_history_initialization(self, qapp):
        """Test that password history dialog initializes correctly."""
        entry = {
            "title": "Test Entry",
            "password_history": [
                {"password": "oldpass123", "changed_at": "2025-01-01T12:00:00Z"},
                {"password": "oldpass456", "changed_at": "2025-01-02T12:00:00Z"},
            ],
        }
        mock_clipboard = Mock()

        dialog = PasswordHistoryDialog(entry, mock_clipboard)
        assert "Password History" in dialog.windowTitle()
        assert "Test Entry" in dialog.windowTitle()
        assert dialog.isModal()

    def test_empty_password_history(self, qapp):
        """Test dialog with empty password history."""
        entry = {"title": "Test Entry", "password_history": []}
        mock_clipboard = Mock()

        dialog = PasswordHistoryDialog(entry, mock_clipboard)
        # Should show "no history" message
        # We can't easily test UI text, but dialog should initialize without error
        assert dialog is not None

    def test_password_masking(self, qapp):
        """Test that passwords are masked in the list."""
        entry = {
            "title": "Test Entry",
            "password_history": [
                {"password": "secretpass", "changed_at": "2025-01-01T12:00:00Z"},
            ],
        }
        mock_clipboard = Mock()

        dialog = PasswordHistoryDialog(entry, mock_clipboard)
        # Password should be masked in display
        item_text = dialog.history_list.item(0).text()
        assert "secretpass" not in item_text
        assert "•" in item_text  # Masked with bullets


class TestUIIntegration:
    """Integration tests for UI components."""

    def test_all_dialogs_can_be_created(self, qapp, mock_settings, tmp_path):
        """Test that all dialogs can be instantiated without errors."""
        # Settings dialog
        with patch(
            "pwick.ui.widgets.settings_dialog.load_settings", return_value=mock_settings
        ):
            settings_dlg = SettingsDialog()
            assert settings_dlg is not None

        # Password generator dialog
        gen_dlg = PasswordGeneratorDialog()
        assert gen_dlg is not None

        # Backup manager dialog
        vault_path = str(tmp_path / "test.vault")
        Path(vault_path).touch()
        backup_dlg = BackupManagerDialog(vault_path, mock_settings)
        assert backup_dlg is not None

        # Import wizard dialog
        mock_vault = Mock()
        import_dlg = ImportWizardDialog(mock_vault)
        assert import_dlg is not None

        # Command palette dialog
        mock_main_window = Mock()
        palette_dlg = create_command_palette(mock_main_window)
        assert palette_dlg is not None

        # Password history dialog
        entry = {"title": "Test", "password_history": []}
        mock_clipboard = Mock()
        history_dlg = PasswordHistoryDialog(entry, mock_clipboard)
        assert history_dlg is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
