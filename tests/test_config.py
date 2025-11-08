"""
Comprehensive unit tests for pwick configuration management.

Tests cover settings loading, saving, validation, and default merging across
all configuration scenarios.
"""

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pwick import config


class TestConfigModule(unittest.TestCase):
    """Test configuration module functionality."""

    def setUp(self):
        """Create temporary directory for test config files."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_get_config_dir = config.get_config_dir

        # Override get_config_dir to use temp directory
        def mock_get_config_dir():
            return Path(self.temp_dir)

        config.get_config_dir = mock_get_config_dir

    def tearDown(self):
        """Clean up temporary files and restore original function."""
        config.get_config_dir = self.original_get_config_dir
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_config_dir(self):
        """Test that config directory path is returned correctly."""
        config_dir = config.get_config_dir()
        self.assertIsInstance(config_dir, Path)
        self.assertEqual(config_dir, Path(self.temp_dir))

    def test_get_config_path(self):
        """Test that config file path is constructed correctly."""
        config_path = config.get_config_path()
        self.assertIsInstance(config_path, Path)
        self.assertEqual(config_path, Path(self.temp_dir) / "settings.toml")

    def test_get_default_settings(self):
        """Test that default settings contain all required keys."""
        defaults = config.get_default_settings()

        # Check essential keys exist
        essential_keys = [
            "auto_lock_minutes",
            "clipboard_clear_seconds",
            "clipboard_history_size",
            "password_generator_length",
            "password_history_limit",
            "password_expiration_days",
            "auto_backup_enabled",
            "theme",
            "log_level",
        ]

        for key in essential_keys:
            self.assertIn(key, defaults, f"Missing default setting: {key}")

        # Check types and reasonable values
        self.assertIsInstance(defaults["auto_lock_minutes"], int)
        self.assertIsInstance(defaults["clipboard_clear_seconds"], int)
        self.assertIsInstance(defaults["theme"], str)
        self.assertIn(defaults["theme"], ["dark", "light"])

    def test_load_settings_nonexistent_file(self):
        """Test loading settings when config file doesn't exist returns defaults."""
        settings = config.load_settings()

        # Should return defaults
        defaults = config.get_default_settings()
        self.assertEqual(settings, defaults)

    def test_save_and_load_settings(self):
        """Test saving and loading settings round-trip."""
        # Skip if tomli_w not available
        if config.tomli_w is None:
            self.skipTest("tomli_w not available")

        test_settings = config.get_default_settings()
        test_settings["auto_lock_minutes"] = 10
        test_settings["theme"] = "light"

        # Save settings
        result = config.save_settings(test_settings)
        self.assertTrue(result, "Failed to save settings")

        # Load settings
        loaded_settings = config.load_settings()

        self.assertEqual(loaded_settings["auto_lock_minutes"], 10)
        self.assertEqual(loaded_settings["theme"], "light")

    def test_load_settings_merges_defaults(self):
        """Test that loading settings merges missing keys from defaults."""
        # Skip if tomli_w not available
        if config.tomli_w is None:
            self.skipTest("tomli_w not available")

        # Create incomplete settings (missing some keys)
        incomplete_settings = {
            "auto_lock_minutes": 15,
            "theme": "dark",
        }

        config.save_settings(incomplete_settings)

        # Load settings
        loaded_settings = config.load_settings()

        # Should have user values
        self.assertEqual(loaded_settings["auto_lock_minutes"], 15)
        self.assertEqual(loaded_settings["theme"], "dark")

        # Should have default values for missing keys
        defaults = config.get_default_settings()
        self.assertEqual(
            loaded_settings["clipboard_clear_seconds"],
            defaults["clipboard_clear_seconds"],
        )
        self.assertEqual(
            loaded_settings["password_generator_length"],
            defaults["password_generator_length"],
        )

    def test_reset_settings(self):
        """Test that reset_settings deletes the config file."""
        # Skip if tomli_w not available
        if config.tomli_w is None:
            self.skipTest("tomli_w not available")

        # Create settings file
        test_settings = config.get_default_settings()
        config.save_settings(test_settings)

        config_path = config.get_config_path()
        self.assertTrue(config_path.exists(), "Config file was not created")

        # Reset settings
        result = config.reset_settings()
        self.assertTrue(result, "Failed to reset settings")

        # Config file should be deleted
        self.assertFalse(config_path.exists(), "Config file was not deleted")

    def test_validate_settings_auto_lock_minutes(self):
        """Test auto_lock_minutes validation."""
        settings = config.get_default_settings()

        # Test negative value (should be corrected to 0)
        settings["auto_lock_minutes"] = -5
        validated = config.validate_settings(settings)
        self.assertEqual(validated["auto_lock_minutes"], 0)

        # Test too large value (should be corrected to 1440)
        settings["auto_lock_minutes"] = 2000
        validated = config.validate_settings(settings)
        self.assertEqual(validated["auto_lock_minutes"], 1440)

        # Test valid value
        settings["auto_lock_minutes"] = 10
        validated = config.validate_settings(settings)
        self.assertEqual(validated["auto_lock_minutes"], 10)

    def test_validate_settings_clipboard_clear_seconds(self):
        """Test clipboard_clear_seconds validation."""
        settings = config.get_default_settings()

        # Test too small value
        settings["clipboard_clear_seconds"] = 5
        validated = config.validate_settings(settings)
        self.assertEqual(validated["clipboard_clear_seconds"], 10)

        # Test too large value
        settings["clipboard_clear_seconds"] = 700
        validated = config.validate_settings(settings)
        self.assertEqual(validated["clipboard_clear_seconds"], 600)

        # Test valid value
        settings["clipboard_clear_seconds"] = 30
        validated = config.validate_settings(settings)
        self.assertEqual(validated["clipboard_clear_seconds"], 30)

    def test_validate_settings_password_generator_length(self):
        """Test password_generator_length validation."""
        settings = config.get_default_settings()

        # Test too small value
        settings["password_generator_length"] = 5
        validated = config.validate_settings(settings)
        self.assertEqual(validated["password_generator_length"], 8)

        # Test too large value
        settings["password_generator_length"] = 200
        validated = config.validate_settings(settings)
        self.assertEqual(validated["password_generator_length"], 128)

        # Test valid value
        settings["password_generator_length"] = 20
        validated = config.validate_settings(settings)
        self.assertEqual(validated["password_generator_length"], 20)

    def test_validate_settings_password_generator_charsets(self):
        """Test that at least one character set is enabled for password generator."""
        settings = config.get_default_settings()

        # Disable all character sets
        settings["password_generator_use_uppercase"] = False
        settings["password_generator_use_lowercase"] = False
        settings["password_generator_use_digits"] = False
        settings["password_generator_use_punctuation"] = False

        validated = config.validate_settings(settings)

        # Should re-enable all character sets
        self.assertTrue(validated["password_generator_use_uppercase"])
        self.assertTrue(validated["password_generator_use_lowercase"])
        self.assertTrue(validated["password_generator_use_digits"])
        self.assertTrue(validated["password_generator_use_punctuation"])

    def test_validate_settings_password_history_limit(self):
        """Test password_history_limit validation."""
        settings = config.get_default_settings()

        # Test too small value
        settings["password_history_limit"] = 0
        validated = config.validate_settings(settings)
        self.assertEqual(validated["password_history_limit"], 1)

        # Test too large value
        settings["password_history_limit"] = 30
        validated = config.validate_settings(settings)
        self.assertEqual(validated["password_history_limit"], 20)

        # Test valid value
        settings["password_history_limit"] = 5
        validated = config.validate_settings(settings)
        self.assertEqual(validated["password_history_limit"], 5)

    def test_validate_settings_theme(self):
        """Test theme validation."""
        settings = config.get_default_settings()

        # Test invalid theme
        settings["theme"] = "rainbow"
        validated = config.validate_settings(settings)
        self.assertEqual(validated["theme"], "dark")  # Should default to dark

        # Test valid themes
        settings["theme"] = "light"
        validated = config.validate_settings(settings)
        self.assertEqual(validated["theme"], "light")

        settings["theme"] = "dark"
        validated = config.validate_settings(settings)
        self.assertEqual(validated["theme"], "dark")

    def test_validate_settings_log_level(self):
        """Test log_level validation."""
        settings = config.get_default_settings()

        # Test invalid log level
        settings["log_level"] = "TRACE"
        validated = config.validate_settings(settings)
        self.assertEqual(validated["log_level"], "INFO")  # Should default to INFO

        # Test valid log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings["log_level"] = level
            validated = config.validate_settings(settings)
            self.assertEqual(validated["log_level"], level)

    def test_validate_settings_auto_backup_frequency(self):
        """Test auto_backup_frequency validation."""
        settings = config.get_default_settings()

        # Test invalid frequency
        settings["auto_backup_frequency"] = "hourly"
        validated = config.validate_settings(settings)
        self.assertEqual(validated["auto_backup_frequency"], "weekly")  # Should default

        # Test valid frequencies
        for freq in ["daily", "weekly", "on_change"]:
            settings["auto_backup_frequency"] = freq
            validated = config.validate_settings(settings)
            self.assertEqual(validated["auto_backup_frequency"], freq)

    def test_validate_settings_argon2_parameters(self):
        """Test Argon2id parameter validation."""
        settings = config.get_default_settings()

        # Test time_cost too small
        settings["vault_argon2_time_cost"] = 0
        validated = config.validate_settings(settings)
        self.assertEqual(validated["vault_argon2_time_cost"], 1)

        # Test time_cost too large
        settings["vault_argon2_time_cost"] = 20
        validated = config.validate_settings(settings)
        self.assertEqual(validated["vault_argon2_time_cost"], 10)

        # Test memory_cost too small
        settings["vault_argon2_memory_cost"] = 1024
        validated = config.validate_settings(settings)
        self.assertEqual(validated["vault_argon2_memory_cost"], 8192)

        # Test memory_cost too large
        settings["vault_argon2_memory_cost"] = 2000000
        validated = config.validate_settings(settings)
        self.assertEqual(validated["vault_argon2_memory_cost"], 1048576)

        # Test parallelism too small
        settings["vault_argon2_parallelism"] = 0
        validated = config.validate_settings(settings)
        self.assertEqual(validated["vault_argon2_parallelism"], 1)

        # Test parallelism too large
        settings["vault_argon2_parallelism"] = 32
        validated = config.validate_settings(settings)
        self.assertEqual(validated["vault_argon2_parallelism"], 16)

    def test_config_directory_creation(self):
        """Test that save_settings creates config directory if it doesn't exist."""
        # Skip if tomli_w not available
        if config.tomli_w is None:
            self.skipTest("tomli_w not available")

        # Remove temp directory
        shutil.rmtree(self.temp_dir)
        self.assertFalse(os.path.exists(self.temp_dir))

        # Save settings
        test_settings = config.get_default_settings()
        result = config.save_settings(test_settings)

        # Directory should be created
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue((Path(self.temp_dir) / "settings.toml").exists())


if __name__ == "__main__":
    unittest.main()
