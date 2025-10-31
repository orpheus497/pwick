"""
Basic unit tests for pwick vault functionality.
"""

import unittest
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pwick import vault


class TestVault(unittest.TestCase):
    """Test vault operations."""
    
    def setUp(self):
        """Create temporary directory for test vaults."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = os.path.join(self.temp_dir, 'test.vault')
        self.master_password = 'TestPassword123!'
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_vault(self):
        """Test creating a new vault."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        
        self.assertIsNotNone(vault_data)
        self.assertIn('metadata', vault_data)
        self.assertIn('entries', vault_data)
        self.assertEqual(vault_data['metadata']['version'], '2.0')
        self.assertEqual(len(vault_data['entries']), 0)
        self.assertTrue(os.path.exists(self.vault_path))
        self.assertIn('argon2_params', vault_data['metadata'])
    
    def test_load_vault(self):
        """Test loading an existing vault."""
        vault.create_vault(self.vault_path, self.master_password)
        loaded_vault = vault.load_vault(self.vault_path, self.master_password)
        
        self.assertIsNotNone(loaded_vault)
        self.assertIn('metadata', loaded_vault)
        self.assertIn('entries', loaded_vault)
    
    def test_wrong_password(self):
        """Test that wrong password raises authentication error."""
        vault.create_vault(self.vault_path, self.master_password)
        
        with self.assertRaises(vault.VaultAuthenticationError):
            vault.load_vault(self.vault_path, 'WrongPassword')
    
    def test_add_entry(self):
        """Test adding an entry to the vault."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        
        entry_id = vault.add_entry(
            vault_data,
            'Test Site',
            'testuser',
            'testpass123',
            'Some notes'
        )
        
        self.assertIsNotNone(entry_id)
        self.assertEqual(len(vault_data['entries']), 1)
        
        entry = vault_data['entries'][0]
        self.assertEqual(entry['id'], entry_id)
        self.assertEqual(entry['title'], 'Test Site')
        self.assertEqual(entry['username'], 'testuser')
        self.assertEqual(entry['password'], 'testpass123')
        self.assertEqual(entry['notes'], 'Some notes')
        self.assertEqual(entry['type'], 'password')

    def test_add_note(self):
        """Test adding a note entry to the vault."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        
        note_id = vault.add_note(
            vault_data,
            'Test Note',
            'This is the content of the note.'
        )
        
        self.assertIsNotNone(note_id)
        self.assertEqual(len(vault_data['entries']), 1)
        
        entry = vault_data['entries'][0]
        self.assertEqual(entry['id'], note_id)
        self.assertEqual(entry['title'], 'Test Note')
        self.assertEqual(entry['notes'], 'This is the content of the note.')
        self.assertEqual(entry['type'], 'note')
        self.assertEqual(entry['username'], '')
        self.assertEqual(entry['password'], '')

    def test_update_entry(self):
        """Test updating an entry."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        entry_id = vault.add_entry(vault_data, 'Test', 'user', 'pass', 'notes')
        
        result = vault.update_entry(
            vault_data,
            entry_id,
            title='Updated Test',
            username='newuser'
        )
        
        self.assertTrue(result)
        entry = vault_data['entries'][0]
        self.assertEqual(entry['title'], 'Updated Test')
        self.assertEqual(entry['username'], 'newuser')
        self.assertEqual(entry['password'], 'pass')  # Unchanged

    def test_update_note(self):
        """Test updating a note entry."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        note_id = vault.add_note(vault_data, 'Test Note', 'Initial content')
        
        result = vault.update_note(
            vault_data,
            note_id,
            title='Updated Note Title',
            content='Updated note content.'
        )
        
        self.assertTrue(result)
        entry = vault_data['entries'][0]
        self.assertEqual(entry['title'], 'Updated Note Title')
        self.assertEqual(entry['notes'], 'Updated note content.')
    
    def test_delete_entry(self):
        """Test deleting an entry."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        entry_id = vault.add_entry(vault_data, 'Test', 'user', 'pass', 'notes')
        
        self.assertEqual(len(vault_data['entries']), 1)
        
        result = vault.delete_entry(vault_data, entry_id)
        
        self.assertTrue(result)
        self.assertEqual(len(vault_data['entries']), 0)
    
    def test_save_and_load_with_entries(self):
        """Test saving and loading a vault with entries."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        
        vault.add_entry(vault_data, 'Site 1', 'user1', 'pass1', 'notes1')
        vault.add_entry(vault_data, 'Site 2', 'user2', 'pass2', 'notes2')
        
        vault.save_vault(self.vault_path, vault_data, self.master_password)
        
        loaded_vault = vault.load_vault(self.vault_path, self.master_password)
        
        self.assertEqual(len(loaded_vault['entries']), 2)
        self.assertEqual(loaded_vault['entries'][0]['title'], 'Site 1')
        self.assertEqual(loaded_vault['entries'][1]['title'], 'Site 2')
    
    def test_export_import(self):
        """Test exporting and importing a vault."""
        vault_data = vault.create_vault(self.vault_path, self.master_password)
        vault.add_entry(vault_data, 'Test', 'user', 'pass', 'notes')
        vault.save_vault(self.vault_path, vault_data, self.master_password)
        
        export_path = os.path.join(self.temp_dir, 'exported.encrypted')
        vault.export_encrypted(self.vault_path, export_path, self.master_password)
        
        self.assertTrue(os.path.exists(export_path))
        
        import_path = os.path.join(self.temp_dir, 'imported.vault')
        imported_vault = vault.import_encrypted(
            export_path, import_path, self.master_password
        )
        
        self.assertEqual(len(imported_vault['entries']), 1)
        self.assertEqual(imported_vault['entries'][0]['title'], 'Test')


if __name__ == '__main__':
    unittest.main()
