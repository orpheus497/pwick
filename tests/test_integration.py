#!/usr/bin/env python3
"""
Integration test for pwick - tests the complete workflow.
"""

import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pwick import vault


def test_complete_workflow():
    """Test a complete workflow of vault operations."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        vault_path = os.path.join(temp_dir, 'test.vault')
        master_password = 'SecurePassword123!'
        
        print("1. Creating vault...")
        vault_data = vault.create_vault(vault_path, master_password)
        print(f"   ✓ Vault created at {vault_path}")
        
        print("\n2. Adding entries...")
        vault.add_entry(vault_data, 'GitHub', 'user@example.com', 'ghp_1234567890', 'Personal GitHub account')
        vault.add_entry(vault_data, 'Email', 'myemail@example.com', 'email_pass_123', 'Primary email')
        vault.add_entry(vault_data, 'Banking', 'john.doe', 'bank_secure_456', '')
        print(f"   ✓ Added 3 entries")
        
        print("\n3. Saving vault...")
        vault.save_vault(vault_path, vault_data, master_password)
        print("   ✓ Vault saved")
        
        print("\n4. Loading vault...")
        loaded_vault = vault.load_vault(vault_path, master_password)
        assert len(loaded_vault['entries']) == 3
        print(f"   ✓ Vault loaded with {len(loaded_vault['entries'])} entries")
        
        print("\n5. Testing wrong password...")
        try:
            vault.load_vault(vault_path, 'WrongPassword')
            print("   ✗ ERROR: Should have raised authentication error!")
            return False
        except vault.VaultAuthenticationError:
            print("   ✓ Correctly rejected wrong password")
        
        print("\n6. Updating an entry...")
        entry_id = loaded_vault['entries'][0]['id']
        vault.update_entry(loaded_vault, entry_id, title='GitHub Updated', notes='Updated notes')
        vault.save_vault(vault_path, loaded_vault, master_password)
        print("   ✓ Entry updated")
        
        print("\n7. Deleting an entry...")
        entry_id_to_delete = loaded_vault['entries'][1]['id']
        vault.delete_entry(loaded_vault, entry_id_to_delete)
        vault.save_vault(vault_path, loaded_vault, master_password)
        print("   ✓ Entry deleted")
        
        print("\n8. Verifying changes...")
        reloaded = vault.load_vault(vault_path, master_password)
        assert len(reloaded['entries']) == 2
        assert reloaded['entries'][0]['title'] == 'GitHub Updated'
        print("   ✓ Changes persisted correctly")
        
        print("\n9. Exporting vault...")
        export_path = os.path.join(temp_dir, 'exported.encrypted')
        vault.export_encrypted(vault_path, export_path, master_password)
        print(f"   ✓ Vault exported to {export_path}")
        
        print("\n10. Importing vault...")
        import_path = os.path.join(temp_dir, 'imported.vault')
        imported = vault.import_encrypted(export_path, import_path, master_password)
        assert len(imported['entries']) == 2
        print(f"   ✓ Vault imported with {len(imported['entries'])} entries")
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✓")
        print("="*50)
        
        # Display entries
        print("\nFinal vault entries:")
        for i, entry in enumerate(imported['entries'], 1):
            print(f"{i}. {entry['title']}")
            print(f"   Username: {entry['username']}")
            print(f"   Password: {'*' * len(entry['password'])}")
            if entry['notes']:
                print(f"   Notes: {entry['notes']}")
        
        return True
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
