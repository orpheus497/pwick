"""
Integration test for pwick - tests the complete workflow.
"""

import unittest
import tempfile
import os
import sys
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pwick import vault


class TestIntegration(unittest.TestCase):
    """Test a complete workflow of vault operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = os.path.join(self.temp_dir, 'test.vault')
        self.master_password = 'SecurePassword123!'

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_complete_workflow(self):
        """Test a complete workflow of vault operations."""
        # 1. Creating vault
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        self.assertIsNotNone(vault_data)

        # 2. Adding entries
        vault.add_entry(vault_data, 'GitHub', 'user@example.com', 'ghp_1234567890', 'Personal GitHub account')
        vault.add_entry(vault_data, 'Email', 'myemail@example.com', 'email_pass_123', 'Primary email')
        vault.add_note(vault_data, 'Shopping List', 'Milk, Bread, Eggs')
        self.assertEqual(len(vault_data['entries']), 3)

        # 3. Saving vault
        vault.save_vault(self.vault_path, vault_data, self.master_password)

        # 4. Loading vault
        loaded_vault = vault.load_vault(self.vault_path, self.master_password)
        self.assertEqual(len(loaded_vault['entries']), 3)

        # 5. Testing wrong password
        with self.assertRaises(vault.VaultAuthenticationError):
            vault.load_vault(self.vault_path, 'WrongPassword')

        # 6. Updating an entry
        entry_id = loaded_vault['entries'][0]['id']
        vault.update_entry(loaded_vault, entry_id, title='GitHub Updated', notes='Updated notes')
        vault.save_vault(self.vault_path, loaded_vault, self.master_password)

        # 7. Deleting an entry
        entry_id_to_delete = loaded_vault['entries'][1]['id']
        vault.delete_entry(loaded_vault, entry_id_to_delete)
        vault.save_vault(self.vault_path, loaded_vault, self.master_password)

        # 8. Verifying changes
        reloaded = vault.load_vault(self.vault_path, self.master_password)
        self.assertEqual(len(reloaded['entries']), 2)
        self.assertEqual(reloaded['entries'][0]['title'], 'GitHub Updated')

        # 9. Exporting vault
        export_path = os.path.join(self.temp_dir, 'exported.encrypted')
        vault.export_encrypted(self.vault_path, export_path, self.master_password)
        self.assertTrue(os.path.exists(export_path))

        # 10. Importing vault
        import_path = os.path.join(self.temp_dir, 'imported.vault')
        imported = vault.import_encrypted(export_path, import_path, self.master_password)
        self.assertEqual(len(imported['entries']), 2)


if __name__ == '__main__':
    unittest.main()