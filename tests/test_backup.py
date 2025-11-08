"""
Comprehensive unit tests for pwick backup management.

Tests cover backup creation, listing, rotation, restoration, and automatic
backup functionality.
"""

import unittest
import tempfile
import shutil
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pwick import vault, backup


class TestBackupModule(unittest.TestCase):
    """Test backup module functionality."""

    def setUp(self):
        """Create temporary directory and test vault."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = os.path.join(self.temp_dir, 'test.vault')
        self.master_password = 'TestPassword123!'

        # Create a test vault
        self.vault_data = vault.create_vault(self.vault_path, self.master_password)
        vault.add_entry(self.vault_data, 'Test Site', 'user', 'pass', 'notes')
        vault.save_vault(self.vault_path, self.vault_data, self.master_password)

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_backup_filename(self):
        """Test backup filename generation includes timestamp."""
        filename = backup.get_backup_filename(self.vault_path)

        self.assertIsInstance(filename, str)
        self.assertTrue(filename.startswith('test_'))
        self.assertTrue(filename.endswith('.vault'))
        self.assertIn('_', filename)  # Should contain timestamp separators

        # Check that timestamp is present (basic format check)
        # Format: test_YYYY-MM-DD_HH-MM-SS.vault
        parts = filename.split('_')
        self.assertEqual(len(parts), 4)  # test, YYYY-MM-DD, HH-MM-SS.vault

    def test_create_backup(self):
        """Test creating a backup file."""
        backup_path = backup.create_backup(self.vault_path)

        self.assertIsNotNone(backup_path, "Backup creation returned None")
        self.assertTrue(os.path.exists(backup_path), "Backup file does not exist")

        # Verify backup is a valid vault file
        loaded = vault.load_vault(backup_path, self.master_password)
        self.assertEqual(len(loaded['entries']), 1)
        self.assertEqual(loaded['entries'][0]['title'], 'Test Site')

    def test_create_backup_custom_directory(self):
        """Test creating backup in custom directory."""
        backup_dir = os.path.join(self.temp_dir, 'backups')

        backup_path = backup.create_backup(self.vault_path, backup_dir)

        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.startswith(backup_dir))
        self.assertTrue(os.path.exists(backup_dir), "Backup directory was not created")

    def test_create_backup_nonexistent_vault(self):
        """Test creating backup of nonexistent vault returns None."""
        nonexistent_path = os.path.join(self.temp_dir, 'nonexistent.vault')

        backup_path = backup.create_backup(nonexistent_path)

        self.assertIsNone(backup_path, "Backup of nonexistent vault should return None")

    def test_list_backups(self):
        """Test listing backup files."""
        # Create multiple backups (with small delays to ensure different timestamps)
        backup1 = backup.create_backup(self.vault_path)
        time.sleep(0.1)
        backup2 = backup.create_backup(self.vault_path)
        time.sleep(0.1)
        backup3 = backup.create_backup(self.vault_path)

        # List backups
        backups = backup.list_backups(self.vault_path)

        self.assertEqual(len(backups), 3, "Should find 3 backups")

        # Verify backups are tuples of (path, datetime)
        for backup_item in backups:
            self.assertIsInstance(backup_item, tuple)
            self.assertEqual(len(backup_item), 2)
            backup_path, backup_time = backup_item
            self.assertIsInstance(backup_path, str)
            self.assertIsInstance(backup_time, datetime)
            self.assertTrue(os.path.exists(backup_path))

        # Verify backups are sorted by time (newest first)
        times = [backup_time for _, backup_time in backups]
        self.assertEqual(times, sorted(times, reverse=True),
                        "Backups should be sorted newest first")

    def test_list_backups_empty(self):
        """Test listing backups when none exist."""
        # Create a new vault with no backups
        new_vault_path = os.path.join(self.temp_dir, 'new_vault.vault')
        vault.create_vault(new_vault_path, self.master_password)

        backups = backup.list_backups(new_vault_path)

        self.assertEqual(len(backups), 0, "Should find no backups")

    def test_list_backups_custom_directory(self):
        """Test listing backups from custom directory."""
        backup_dir = os.path.join(self.temp_dir, 'backups')

        # Create backups in custom directory
        backup.create_backup(self.vault_path, backup_dir)
        backup.create_backup(self.vault_path, backup_dir)

        # List from custom directory
        backups = backup.list_backups(self.vault_path, backup_dir)

        self.assertEqual(len(backups), 2)

        # List from default directory (should be empty)
        default_backups = backup.list_backups(self.vault_path)
        self.assertEqual(len(default_backups), 0)

    def test_cleanup_old_backups(self):
        """Test cleaning up old backup files."""
        # Create 7 backups
        for i in range(7):
            backup.create_backup(self.vault_path)
            time.sleep(0.05)  # Small delay to ensure different timestamps

        # Verify 7 backups exist
        backups_before = backup.list_backups(self.vault_path)
        self.assertEqual(len(backups_before), 7)

        # Keep only 3 most recent
        deleted_count = backup.cleanup_old_backups(self.vault_path, keep_count=3)

        self.assertEqual(deleted_count, 4, "Should delete 4 old backups")

        # Verify only 3 remain
        backups_after = backup.list_backups(self.vault_path)
        self.assertEqual(len(backups_after), 3)

        # Verify the 3 newest were kept
        for backup_path, _ in backups_after:
            self.assertTrue(os.path.exists(backup_path))

    def test_cleanup_old_backups_keep_all(self):
        """Test cleanup when keep_count is larger than backup count."""
        # Create 3 backups
        for i in range(3):
            backup.create_backup(self.vault_path)
            time.sleep(0.05)

        # Keep 5 (more than exist)
        deleted_count = backup.cleanup_old_backups(self.vault_path, keep_count=5)

        self.assertEqual(deleted_count, 0, "Should delete 0 backups")

        # Verify all 3 still exist
        backups = backup.list_backups(self.vault_path)
        self.assertEqual(len(backups), 3)

    def test_restore_backup(self):
        """Test restoring vault from backup."""
        # Create backup
        backup_path = backup.create_backup(self.vault_path)

        # Modify original vault
        vault_data = vault.load_vault(self.vault_path, self.master_password)
        vault.add_entry(vault_data, 'New Entry', 'newuser', 'newpass', 'newnotes')
        vault.save_vault(self.vault_path, vault_data, self.master_password)

        # Verify original has 2 entries
        modified_vault = vault.load_vault(self.vault_path, self.master_password)
        self.assertEqual(len(modified_vault['entries']), 2)

        # Restore from backup
        restore_path = os.path.join(self.temp_dir, 'restored.vault')
        result = backup.restore_backup(backup_path, restore_path)

        self.assertTrue(result, "Restore should succeed")
        self.assertTrue(os.path.exists(restore_path))

        # Verify restored vault has only 1 entry (original state)
        restored_vault = vault.load_vault(restore_path, self.master_password)
        self.assertEqual(len(restored_vault['entries']), 1)
        self.assertEqual(restored_vault['entries'][0]['title'], 'Test Site')

    def test_restore_backup_nonexistent(self):
        """Test restoring from nonexistent backup returns False."""
        nonexistent_backup = os.path.join(self.temp_dir, 'nonexistent_backup.vault')
        restore_path = os.path.join(self.temp_dir, 'restored.vault')

        result = backup.restore_backup(nonexistent_backup, restore_path)

        self.assertFalse(result, "Restore of nonexistent backup should return False")
        self.assertFalse(os.path.exists(restore_path))

    def test_should_create_backup_on_change(self):
        """Test should_create_backup with 'on_change' frequency."""
        # Always returns True for on_change
        result = backup.should_create_backup(
            self.vault_path,
            frequency='on_change',
            last_backup_time=datetime.now()
        )
        self.assertTrue(result)

    def test_should_create_backup_no_previous_backup(self):
        """Test should_create_backup when no previous backup exists."""
        # Should return True when last_backup_time is None
        result = backup.should_create_backup(
            self.vault_path,
            frequency='daily',
            last_backup_time=None
        )
        self.assertTrue(result)

    def test_should_create_backup_daily(self):
        """Test should_create_backup with 'daily' frequency."""
        # Recent backup (1 hour ago) - should not create
        recent_backup = datetime.now() - timedelta(hours=1)
        result = backup.should_create_backup(
            self.vault_path,
            frequency='daily',
            last_backup_time=recent_backup
        )
        self.assertFalse(result)

        # Old backup (2 days ago) - should create
        old_backup = datetime.now() - timedelta(days=2)
        result = backup.should_create_backup(
            self.vault_path,
            frequency='daily',
            last_backup_time=old_backup
        )
        self.assertTrue(result)

    def test_should_create_backup_weekly(self):
        """Test should_create_backup with 'weekly' frequency."""
        # Recent backup (3 days ago) - should not create
        recent_backup = datetime.now() - timedelta(days=3)
        result = backup.should_create_backup(
            self.vault_path,
            frequency='weekly',
            last_backup_time=recent_backup
        )
        self.assertFalse(result)

        # Old backup (8 days ago) - should create
        old_backup = datetime.now() - timedelta(days=8)
        result = backup.should_create_backup(
            self.vault_path,
            frequency='weekly',
            last_backup_time=old_backup
        )
        self.assertTrue(result)

    def test_get_backup_size(self):
        """Test calculating total size of all backups."""
        # Create some backups
        backup.create_backup(self.vault_path)
        backup.create_backup(self.vault_path)
        backup.create_backup(self.vault_path)

        total_size = backup.get_backup_size(self.vault_path)

        self.assertIsInstance(total_size, int)
        self.assertGreater(total_size, 0, "Total backup size should be greater than 0")

        # Size should be approximately 3x the original vault size
        vault_size = os.path.getsize(self.vault_path)
        self.assertAlmostEqual(total_size, vault_size * 3, delta=vault_size * 0.5)

    def test_get_backup_size_no_backups(self):
        """Test getting backup size when no backups exist."""
        new_vault_path = os.path.join(self.temp_dir, 'new_vault.vault')
        vault.create_vault(new_vault_path, self.master_password)

        total_size = backup.get_backup_size(new_vault_path)

        self.assertEqual(total_size, 0)

    def test_auto_backup_disabled(self):
        """Test auto_backup when backup is disabled in settings."""
        test_settings = {
            'auto_backup_enabled': False,
            'auto_backup_location': '',
            'auto_backup_frequency': 'weekly',
            'auto_backup_keep_count': 5,
        }

        backup_path = backup.auto_backup(self.vault_path, test_settings)

        self.assertIsNone(backup_path, "Auto-backup should return None when disabled")

        # Verify no backup was created
        backups = backup.list_backups(self.vault_path)
        self.assertEqual(len(backups), 0)

    def test_auto_backup_enabled(self):
        """Test auto_backup when backup is enabled in settings."""
        test_settings = {
            'auto_backup_enabled': True,
            'auto_backup_location': '',  # Use default location
            'auto_backup_frequency': 'on_change',
            'auto_backup_keep_count': 5,
        }

        backup_path = backup.auto_backup(self.vault_path, test_settings)

        self.assertIsNotNone(backup_path, "Auto-backup should create a backup")
        self.assertTrue(os.path.exists(backup_path))

    def test_auto_backup_with_rotation(self):
        """Test auto_backup performs rotation of old backups."""
        test_settings = {
            'auto_backup_enabled': True,
            'auto_backup_location': '',
            'auto_backup_frequency': 'on_change',
            'auto_backup_keep_count': 3,
        }

        # Create 5 backups
        for i in range(5):
            backup.auto_backup(self.vault_path, test_settings)
            time.sleep(0.05)

        # Should only keep 3 most recent
        backups = backup.list_backups(self.vault_path)
        self.assertEqual(len(backups), 3, "Should keep only 3 most recent backups")

    def test_auto_backup_custom_location(self):
        """Test auto_backup with custom backup location."""
        backup_dir = os.path.join(self.temp_dir, 'custom_backups')

        test_settings = {
            'auto_backup_enabled': True,
            'auto_backup_location': backup_dir,
            'auto_backup_frequency': 'on_change',
            'auto_backup_keep_count': 5,
        }

        backup_path = backup.auto_backup(self.vault_path, test_settings)

        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.startswith(backup_dir))
        self.assertTrue(os.path.exists(backup_dir))

        # Verify backup is in custom location
        backups = backup.list_backups(self.vault_path, backup_dir)
        self.assertEqual(len(backups), 1)


if __name__ == '__main__':
    unittest.main()
