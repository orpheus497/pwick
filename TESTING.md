# Testing Guide for pwick

This document describes how to test the pwick password manager application.

## Prerequisites

Make sure you have set up the development environment:

```bash
./build.sh
# Or manually:
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running Tests

### Unit Tests

The unit tests cover the core vault functionality including encryption, decryption, and entry management:

```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m unittest tests.test_vault -v
```

Expected output:
```
test_add_entry ... ok
test_create_vault ... ok
test_delete_entry ... ok
test_export_import ... ok
test_load_vault ... ok
test_save_and_load_with_entries ... ok
test_update_entry ... ok
test_wrong_password ... ok

----------------------------------------------------------------------
Ran 8 tests in X.XXXs

OK
```

### Integration Tests

The integration test runs through a complete workflow:

```bash
source venv/bin/activate
python tests/test_integration.py
```

This test:
1. Creates a new vault
2. Adds multiple entries
3. Saves and loads the vault
4. Tests authentication with wrong password
5. Updates and deletes entries
6. Exports and imports the vault
7. Verifies data integrity

### Manual Testing

To manually test the GUI application:

1. Start the application:
   ```bash
   source venv/bin/activate
   python -m src.pwick
   ```

2. Test the following workflows:

#### First-Time Setup
- Click "Create New Vault"
- Choose a location and name for your vault file
- Enter a master password (confirm it)
- Verify the main window opens

#### Add Entry
- Click "Add" button
- Fill in title, username, password, notes
- Test the "Generate" button for password generation
- Test the "Show" checkbox for password visibility
- Save the entry

#### Edit Entry
- Select an entry from the list
- Click "Edit" button
- Modify any field
- Save changes

#### Copy Password
- Select an entry
- Click "Copy Password"
- Verify the status bar shows "Password copied to clipboard!"
- Paste in another application to verify

#### Delete Entry
- Select an entry
- Click "Delete"
- Confirm the deletion
- Verify entry is removed

#### Export/Import
- Click "Export Vault"
- Save to a .encrypted file
- Lock the vault
- Choose "Import Existing Vault"
- Select the exported file
- Enter your master password
- Verify all data is intact

#### Lock/Unlock
- Click "Lock" to lock the vault
- Reopen with "Open Existing Vault"
- Enter your master password

## Testing Security Features

### Password Strength
Test that the application correctly:
- Rejects empty master passwords
- Confirms password on vault creation
- Rejects wrong passwords on vault open

### Encryption Verification
1. Create a vault with a known password
2. Open the vault file in a text editor
3. Verify that no plaintext passwords or entries are visible
4. Verify the file contains encrypted data (base64-encoded)

### Key Derivation
The vault uses Argon2id with these parameters:
- Time cost: 3 iterations
- Memory cost: 65536 KB (64 MB)
- Parallelism: 1 thread
- Salt: 16 random bytes per vault

This should make vault opening take 1-2 seconds on modern hardware, providing protection against brute-force attacks.

## Platform-Specific Testing

### Linux
```bash
# Test on Ubuntu/Debian
./build.sh
python -m src.pwick

# Test permissions
chmod 600 myvault.vault  # Should still work
chmod 400 myvault.vault  # Should work (read-only)
chmod 000 myvault.vault  # Should fail gracefully
```

### Windows
```cmd
# Test on Windows 10/11
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m src.pwick

# Test with Windows file paths
# Test with network drives (if applicable)
```

## Performance Testing

Test vault operations with various sizes:

```python
# Create a vault with many entries
import sys
sys.path.insert(0, 'src')
from pwick import vault

vault_data = vault.create_vault('large_test.vault', 'password')
for i in range(1000):
    vault.add_entry(vault_data, f'Entry {i}', f'user{i}', f'pass{i}', '')
vault.save_vault('large_test.vault', vault_data, 'password')

# Time the load operation
import time
start = time.time()
loaded = vault.load_vault('large_test.vault', 'password')
print(f"Loaded {len(loaded['entries'])} entries in {time.time() - start:.2f} seconds")
```

## Troubleshooting Tests

### Qt Platform Plugin Issues
If you get "Could not load the Qt platform plugin" errors:
```bash
export QT_QPA_PLATFORM=offscreen  # For headless testing
# Or
export QT_DEBUG_PLUGINS=1  # For debugging
```

### Import Errors
If you get "ModuleNotFoundError":
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Make sure you're in the project root
cd /path/to/pwick

# Try with PYTHONPATH
PYTHONPATH=src python -m unittest tests.test_vault
```

### Cryptography Errors
If you get cryptography-related errors:
```bash
# Reinstall cryptography
pip uninstall cryptography
pip install cryptography==41.0.7
```

## Continuous Testing

For development, you can run tests automatically on file changes using a tool like `pytest-watch`:

```bash
pip install pytest pytest-watch
ptw tests/
```

## Code Coverage

To measure test coverage:

```bash
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report
```

Expected coverage:
- vault.py: >90%
- ui.py: Partial (GUI testing is limited in automated tests)
- __init__.py, __main__.py: 100%
