"""
pwick.backup - Automatic backup management for vault files.

Provides functionality for creating timestamped backups, rotating old backups,
and restoring from backup files. Supports scheduled automatic backups to prevent
data loss from user forgetfulness or system failures.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from .config import load_settings

logger = logging.getLogger(__name__)


def get_backup_filename(vault_path: str) -> str:
    """
    Generate a timestamped backup filename for a vault.

    Args:
        vault_path: Path to the original vault file

    Returns:
        Filename with timestamp (e.g., "myvault_2025-11-08_14-30-00.vault")

    Example:
        >>> get_backup_filename("/path/to/myvault.vault")
        'myvault_2025-11-08_14-30-00.vault'
    """
    vault_file = Path(vault_path)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{vault_file.stem}_{timestamp}{vault_file.suffix}"


def create_backup(vault_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
    """
    Create a timestamped backup of the vault file.

    Args:
        vault_path: Path to the vault file to backup
        backup_dir: Directory to store backup (default: same directory as vault)

    Returns:
        Path to the created backup file, or None if backup failed

    Example:
        >>> backup_path = create_backup("/path/to/vault.vault")
        >>> print(f"Backup created: {backup_path}")
    """
    try:
        vault_file = Path(vault_path)

        if not vault_file.exists():
            logger.error(f"Cannot backup: vault file not found: {vault_path}")
            return None

        # Determine backup directory
        if backup_dir is None:
            backup_dir = vault_file.parent
        else:
            backup_dir = Path(backup_dir)
            backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate backup filename
        backup_filename = get_backup_filename(vault_path)
        backup_path = backup_dir / backup_filename

        # Copy vault file to backup location
        shutil.copy2(vault_path, backup_path)

        logger.info(f"Backup created: {backup_path}")
        return str(backup_path)

    except Exception as e:
        logger.error(f"Failed to create backup: {e}", exc_info=True)
        return None


def list_backups(
    vault_path: str, backup_dir: Optional[str] = None
) -> List[Tuple[str, datetime]]:
    """
    List all backups for a specific vault.

    Args:
        vault_path: Path to the vault file
        backup_dir: Directory where backups are stored (default: same directory as vault)

    Returns:
        List of (backup_path, creation_time) tuples, sorted by creation time (newest first)

    Example:
        >>> backups = list_backups("/path/to/vault.vault")
        >>> for backup_path, creation_time in backups:
        ...     print(f"{creation_time}: {backup_path}")
    """
    try:
        vault_file = Path(vault_path)

        # Determine backup directory
        if backup_dir is None:
            backup_dir = vault_file.parent
        else:
            backup_dir = Path(backup_dir)

        if not backup_dir.exists():
            return []

        # Find all backup files matching the pattern
        pattern = f"{vault_file.stem}_*{vault_file.suffix}"
        backups = []

        for backup_file in backup_dir.glob(pattern):
            if backup_file.is_file():
                # Get file modification time
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                backups.append((str(backup_file), mtime))

        # Sort by creation time, newest first
        backups.sort(key=lambda x: x[1], reverse=True)

        return backups

    except Exception as e:
        logger.error(f"Failed to list backups: {e}", exc_info=True)
        return []


def cleanup_old_backups(
    vault_path: str, backup_dir: Optional[str] = None, keep_count: int = 5
) -> int:
    """
    Remove old backup files, keeping only the most recent N backups.

    Args:
        vault_path: Path to the vault file
        backup_dir: Directory where backups are stored (default: same directory as vault)
        keep_count: Number of most recent backups to keep

    Returns:
        Number of backup files deleted

    Example:
        >>> deleted = cleanup_old_backups("/path/to/vault.vault", keep_count=5)
        >>> print(f"Deleted {deleted} old backups")
    """
    try:
        backups = list_backups(vault_path, backup_dir)

        if len(backups) <= keep_count:
            return 0

        # Delete old backups beyond keep_count
        deleted_count = 0
        for backup_path, _ in backups[keep_count:]:
            try:
                Path(backup_path).unlink()
                deleted_count += 1
                logger.info(f"Deleted old backup: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to delete backup {backup_path}: {e}")

        return deleted_count

    except Exception as e:
        logger.error(f"Failed to cleanup old backups: {e}", exc_info=True)
        return 0


def restore_backup(backup_path: str, target_path: str) -> bool:
    """
    Restore a vault from a backup file.

    Args:
        backup_path: Path to the backup file
        target_path: Path where the vault should be restored

    Returns:
        True if restoration was successful, False otherwise

    Warning:
        This will OVERWRITE the file at target_path if it exists.

    Example:
        >>> success = restore_backup("/path/to/backup.vault", "/path/to/vault.vault")
        >>> if success:
        ...     print("Vault restored successfully")
    """
    try:
        backup_file = Path(backup_path)

        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False

        # Copy backup to target location
        shutil.copy2(backup_path, target_path)

        logger.info(f"Vault restored from backup: {backup_path} -> {target_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to restore backup: {e}", exc_info=True)
        return False


def should_create_backup(
    vault_path: str, frequency: str, last_backup_time: Optional[datetime] = None
) -> bool:
    """
    Determine if a backup should be created based on frequency settings.

    Args:
        vault_path: Path to the vault file
        frequency: Backup frequency ("daily", "weekly", "on_change")
        last_backup_time: Time of last backup (None to always backup)

    Returns:
        True if a backup should be created, False otherwise

    Example:
        >>> if should_create_backup("/path/to/vault.vault", "daily"):
        ...     create_backup("/path/to/vault.vault")
    """
    if frequency == "on_change":
        # Always backup on change
        return True

    if last_backup_time is None:
        # No previous backup, create one
        return True

    now = datetime.now()
    time_since_backup = now - last_backup_time

    if frequency == "daily":
        return time_since_backup >= timedelta(days=1)
    elif frequency == "weekly":
        return time_since_backup >= timedelta(weeks=1)
    else:
        # Unknown frequency, default to daily
        return time_since_backup >= timedelta(days=1)


def get_backup_size(vault_path: str, backup_dir: Optional[str] = None) -> int:
    """
    Get the total size of all backups for a vault in bytes.

    Args:
        vault_path: Path to the vault file
        backup_dir: Directory where backups are stored

    Returns:
        Total size of all backup files in bytes

    Example:
        >>> size_mb = get_backup_size("/path/to/vault.vault") / (1024 * 1024)
        >>> print(f"Total backup size: {size_mb:.2f} MB")
    """
    try:
        backups = list_backups(vault_path, backup_dir)
        total_size = 0

        for backup_path, _ in backups:
            total_size += Path(backup_path).stat().st_size

        return total_size

    except Exception as e:
        logger.error(f"Failed to calculate backup size: {e}", exc_info=True)
        return 0


def auto_backup(vault_path: str, settings: Optional[dict] = None) -> Optional[str]:
    """
    Perform automatic backup based on settings.

    Reads backup settings and creates/manages backups automatically.

    Args:
        vault_path: Path to the vault file
        settings: Settings dictionary (default: load from config)

    Returns:
        Path to created backup, or None if backup was not created or failed

    Example:
        >>> backup_path = auto_backup("/path/to/vault.vault")
        >>> if backup_path:
        ...     print(f"Auto-backup created: {backup_path}")
    """
    try:
        if settings is None:
            settings = load_settings()

        # Check if auto-backup is enabled
        if not settings.get("auto_backup_enabled", False):
            return None

        # Get backup settings
        backup_location = settings.get("auto_backup_location", "")
        keep_count = settings.get("auto_backup_keep_count", 5)

        # Use custom backup location if specified
        backup_dir = backup_location if backup_location else None

        # Create backup
        backup_path = create_backup(vault_path, backup_dir)

        if backup_path:
            # Cleanup old backups
            deleted = cleanup_old_backups(vault_path, backup_dir, keep_count)
            logger.info(
                f"Auto-backup completed: {backup_path} (deleted {deleted} old backups)"
            )

        return backup_path

    except Exception as e:
        logger.error(f"Auto-backup failed: {e}", exc_info=True)
        return None
