"""
pwick.logging_config - Centralized logging configuration for pwick.

Provides structured logging with rotation, configurable levels, and
sensitive data sanitization to prevent password leakage in logs.
"""

import logging
import logging.handlers
import os
import re
from pathlib import Path
from typing import Optional

from .config import get_config_dir


# Sensitive data patterns to sanitize from logs
SENSITIVE_PATTERNS = [
    (re.compile(r'"password":\s*"[^"]*"'), '"password": "***REDACTED***"'),
    (re.compile(r'"master_password":\s*"[^"]*"'), '"master_password": "***REDACTED***"'),
    (re.compile(r'password=\S+'), 'password=***REDACTED***'),
    (re.compile(r'master_password=\S+'), 'master_password=***REDACTED***'),
]


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that sanitizes sensitive data from log messages.

    Prevents passwords, master passwords, and other sensitive information
    from being written to log files.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record, sanitizing sensitive data.

        Args:
            record: Log record to filter

        Returns:
            True to allow the record to be logged (always returns True,
            but modifies the record in place)
        """
        # Sanitize the message
        message = record.getMessage()
        for pattern, replacement in SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)

        # Update the record's message
        record.msg = message
        record.args = ()  # Clear args since we've already formatted the message

        return True


def get_log_path() -> Path:
    """
    Get the path to the log file.

    Returns:
        Path object pointing to pwick.log in the config directory
    """
    config_dir = get_config_dir()
    return config_dir / 'pwick.log'


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Vault loaded successfully")
    """
    return logging.getLogger(name)


def setup_logging(level: str = "INFO", max_bytes: int = 10 * 1024 * 1024,
                  backup_count: int = 3) -> None:
    """
    Configure logging for the application.

    Sets up a rotating file handler that writes to the user's config directory,
    with automatic log rotation and sensitive data filtering.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 3)

    Example:
        >>> setup_logging(level="DEBUG", max_bytes=5*1024*1024)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Get log file path
    log_path = get_log_path()

    # Ensure config directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Add sensitive data filter
    file_handler.addFilter(SensitiveDataFilter())

    # Add handler to root logger
    root_logger.addHandler(file_handler)

    # Also add console handler for development/debugging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)

    # Log startup
    logger = get_logger(__name__)
    logger.info(f"Logging initialized - Level: {level}, Log file: {log_path}")


def clear_logs() -> bool:
    """
    Clear all log files.

    Deletes the main log file and all rotated backups.

    Returns:
        True if logs were cleared successfully, False otherwise
    """
    try:
        log_path = get_log_path()

        # Remove main log file
        if log_path.exists():
            log_path.unlink()

        # Remove backup log files (*.log.1, *.log.2, etc.)
        for backup_file in log_path.parent.glob(f"{log_path.name}.*"):
            if backup_file.is_file():
                backup_file.unlink()

        logger = get_logger(__name__)
        logger.info("Log files cleared")
        return True
    except Exception as e:
        print(f"Error clearing logs: {e}")
        return False


def get_log_size() -> int:
    """
    Get the total size of all log files in bytes.

    Returns:
        Total size of log files in bytes
    """
    try:
        log_path = get_log_path()
        total_size = 0

        # Add main log file size
        if log_path.exists():
            total_size += log_path.stat().st_size

        # Add backup log file sizes
        for backup_file in log_path.parent.glob(f"{log_path.name}.*"):
            if backup_file.is_file():
                total_size += backup_file.stat().st_size

        return total_size
    except Exception:
        return 0
