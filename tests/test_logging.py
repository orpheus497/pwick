"""
Comprehensive unit tests for pwick logging configuration.

Tests cover logging setup, sensitive data sanitization, log rotation,
and log management functionality.
"""

import unittest
import tempfile
import shutil
import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pwick import logging_config, config


class TestLoggingModule(unittest.TestCase):
    """Test logging module functionality."""

    def setUp(self):
        """Create temporary directory for test log files."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_get_config_dir = config.get_config_dir

        # Override get_config_dir to use temp directory
        def mock_get_config_dir():
            return Path(self.temp_dir)

        config.get_config_dir = mock_get_config_dir
        logging_config.get_config_dir = mock_get_config_dir

        # Clear any existing loggers
        logging.root.handlers = []

    def tearDown(self):
        """Clean up temporary files and restore original function."""
        config.get_config_dir = self.original_get_config_dir
        logging_config.get_config_dir = self.original_get_config_dir

        # Clear loggers
        logging.root.handlers = []

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_log_path(self):
        """Test that log file path is constructed correctly."""
        log_path = logging_config.get_log_path()

        self.assertIsInstance(log_path, Path)
        self.assertEqual(log_path, Path(self.temp_dir) / "pwick.log")

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = logging_config.get_logger("test_module")

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_module")

    def test_setup_logging_creates_log_file(self):
        """Test that setup_logging creates log file."""
        logging_config.setup_logging(level="INFO")

        log_path = logging_config.get_log_path()
        self.assertTrue(log_path.parent.exists(), "Log directory should be created")

        # Write a log message
        logger = logging_config.get_logger("test")
        logger.info("Test message")

        # Check that log file was created and contains message
        self.assertTrue(log_path.exists(), "Log file should be created")

        with open(log_path, "r") as f:
            log_content = f.read()
            self.assertIn("Test message", log_content)

    def test_setup_logging_levels(self):
        """Test that logging levels are set correctly."""
        # Test DEBUG level
        logging_config.setup_logging(level="DEBUG")
        logger = logging_config.get_logger("test_debug")

        logger.debug("Debug message")
        logger.info("Info message")

        log_path = logging_config.get_log_path()
        with open(log_path, "r") as f:
            log_content = f.read()
            self.assertIn("Debug message", log_content)
            self.assertIn("Info message", log_content)

    def test_setup_logging_warning_level(self):
        """Test that WARNING level filters out DEBUG and INFO."""
        logging_config.setup_logging(level="WARNING")
        logger = logging_config.get_logger("test_warning")

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        log_path = logging_config.get_log_path()
        with open(log_path, "r") as f:
            log_content = f.read()
            self.assertNotIn("Debug message", log_content)
            self.assertNotIn("Info message", log_content)
            self.assertIn("Warning message", log_content)
            self.assertIn("Error message", log_content)

    def test_sensitive_data_filter_password(self):
        """Test that password fields are sanitized in logs."""
        logging_config.setup_logging(level="INFO")
        logger = logging_config.get_logger("test_sensitive")

        # Log message containing password
        logger.info('User data: {"username": "test", "password": "secret123"}')

        log_path = logging_config.get_log_path()
        with open(log_path, "r") as f:
            log_content = f.read()
            self.assertIn("***REDACTED***", log_content)
            self.assertNotIn("secret123", log_content)

    def test_sensitive_data_filter_master_password(self):
        """Test that master_password fields are sanitized in logs."""
        logging_config.setup_logging(level="INFO")
        logger = logging_config.get_logger("test_master_password")

        # Log message containing master_password
        logger.info('Auth: {"user": "test", "master_password": "supersecret"}')

        log_path = logging_config.get_log_path()
        with open(log_path, "r") as f:
            log_content = f.read()
            self.assertIn("***REDACTED***", log_content)
            self.assertNotIn("supersecret", log_content)

    def test_sensitive_data_filter_multiple_patterns(self):
        """Test that multiple sensitive patterns are sanitized."""
        logging_config.setup_logging(level="INFO")
        logger = logging_config.get_logger("test_multiple")

        # Log with multiple sensitive fields
        logger.info('Data: {"password": "pass1", "master_password": "pass2"}')

        log_path = logging_config.get_log_path()
        with open(log_path, "r") as f:
            log_content = f.read()
            # Both passwords should be redacted
            self.assertEqual(log_content.count("***REDACTED***"), 2)
            self.assertNotIn("pass1", log_content)
            self.assertNotIn("pass2", log_content)

    def test_sensitive_data_filter_preserves_other_data(self):
        """Test that non-sensitive data is not modified."""
        logging_config.setup_logging(level="INFO")
        logger = logging_config.get_logger("test_preserve")

        # Log with sensitive and non-sensitive data
        logger.info(
            'Entry: {"title": "MySite", "username": "user123", "password": "secret"}'
        )

        log_path = logging_config.get_log_path()
        with open(log_path, "r") as f:
            log_content = f.read()
            # Non-sensitive data preserved
            self.assertIn("MySite", log_content)
            self.assertIn("user123", log_content)
            # Sensitive data redacted
            self.assertIn("***REDACTED***", log_content)
            self.assertNotIn("secret", log_content)

    def test_clear_logs(self):
        """Test clearing all log files."""
        # Create log file
        logging_config.setup_logging(level="INFO")
        logger = logging_config.get_logger("test_clear")
        logger.info("Test message")

        log_path = logging_config.get_log_path()
        self.assertTrue(log_path.exists())

        # Clear logs
        result = logging_config.clear_logs()

        self.assertTrue(result, "clear_logs should return True")
        self.assertFalse(log_path.exists(), "Log file should be deleted")

    def test_clear_logs_with_rotated_files(self):
        """Test clearing logs including rotated backup files."""
        logging_config.setup_logging(level="INFO", max_bytes=100, backup_count=3)
        logger = logging_config.get_logger("test_rotation")

        # Write enough to trigger rotation
        for i in range(100):
            logger.info(f"Log message {i} " + "x" * 50)

        log_path = logging_config.get_log_path()

        # Check for rotated files
        rotated_files = list(log_path.parent.glob(f"{log_path.name}.*"))
        self.assertGreater(len(rotated_files), 0, "Should have rotated log files")

        # Clear all logs
        result = logging_config.clear_logs()

        self.assertTrue(result)
        self.assertFalse(log_path.exists(), "Main log should be deleted")

        # Check that rotated files are also deleted
        rotated_files_after = list(log_path.parent.glob(f"{log_path.name}.*"))
        self.assertEqual(len(rotated_files_after), 0, "Rotated logs should be deleted")

    def test_get_log_size(self):
        """Test getting total size of log files."""
        logging_config.setup_logging(level="INFO")
        logger = logging_config.get_logger("test_size")

        # Write some log messages
        for i in range(10):
            logger.info(f"Test message {i}")

        total_size = logging_config.get_log_size()

        self.assertIsInstance(total_size, int)
        self.assertGreater(total_size, 0, "Log size should be greater than 0")

    def test_get_log_size_no_logs(self):
        """Test getting log size when no log files exist."""
        # Don't create any logs

        total_size = logging_config.get_log_size()

        self.assertEqual(total_size, 0, "Log size should be 0 when no logs exist")

    def test_get_log_size_with_rotated_files(self):
        """Test that get_log_size includes rotated log files."""
        logging_config.setup_logging(level="INFO", max_bytes=200, backup_count=3)
        logger = logging_config.get_logger("test_size_rotation")

        # Write enough to trigger rotation
        for i in range(100):
            logger.info(f"Log message {i} " + "x" * 50)

        total_size = logging_config.get_log_size()

        log_path = logging_config.get_log_path()

        # Calculate expected size (main log + rotated logs)
        expected_size = 0
        if log_path.exists():
            expected_size += log_path.stat().st_size

        for rotated_file in log_path.parent.glob(f"{log_path.name}.*"):
            if rotated_file.is_file():
                expected_size += rotated_file.stat().st_size

        self.assertEqual(
            total_size, expected_size, "Total size should include all log files"
        )

    def test_logging_format(self):
        """Test that log messages have correct format."""
        logging_config.setup_logging(level="INFO")
        logger = logging_config.get_logger("test_format")

        logger.info("Test message with format")

        log_path = logging_config.get_log_path()
        with open(log_path, "r") as f:
            log_content = f.read()
            # Should include timestamp, logger name, level, and message
            self.assertRegex(
                log_content,
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*test_format.*INFO.*Test message with format",
            )

    def test_logging_no_duplicate_handlers(self):
        """Test that calling setup_logging multiple times doesn't create duplicate handlers."""
        # Setup logging twice
        logging_config.setup_logging(level="INFO")
        handler_count_1 = len(logging.root.handlers)

        logging_config.setup_logging(level="INFO")
        handler_count_2 = len(logging.root.handlers)

        self.assertEqual(
            handler_count_1, handler_count_2, "Should not create duplicate handlers"
        )

    def test_log_rotation(self):
        """Test that log rotation works correctly."""
        # Setup with small max_bytes to trigger rotation
        logging_config.setup_logging(level="INFO", max_bytes=500, backup_count=2)
        logger = logging_config.get_logger("test_rotation_check")

        # Write enough messages to trigger rotation
        for i in range(50):
            logger.info(f"Log message number {i} with some content to increase size")

        log_path = logging_config.get_log_path()

        # Check that rotated files exist
        rotated_files = list(log_path.parent.glob(f"{log_path.name}.*"))
        self.assertGreater(
            len(rotated_files), 0, "Should have created rotated log files"
        )
        self.assertLessEqual(len(rotated_files), 2, "Should respect backup_count")


if __name__ == "__main__":
    unittest.main()
