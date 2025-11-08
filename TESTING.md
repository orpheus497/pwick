# Testing Guide for pwick

This document describes the testing procedures and guidelines for the pwick password manager project.

---

## Table of Contents

1. [Overview](#overview)
2. [Test Categories](#test-categories)
3. [Running Tests](#running-tests)
4. [Unit Testing](#unit-testing)
5. [Integration Testing](#integration-testing)
6. [Security Testing](#security-testing)
7. [Manual Testing](#manual-testing)
8. [Code Coverage](#code-coverage)
9. [Continuous Integration](#continuous-integration)

---

## Overview

pwick uses a multi-layered testing approach to ensure reliability, security, and correctness. Testing is critical for a security-focused application handling sensitive user data.

**Testing Philosophy:**
- Test security-critical code thoroughly
- Maintain high code coverage (target: >80%)
- Automate where possible, manual test where necessary
- Test backwards compatibility rigorously
- Verify encryption and key derivation

---

## Test Categories

### 1. Unit Tests
Individual functions and methods tested in isolation.

**Coverage:**
- Vault core functionality (`vault.py`)
- Configuration management (`config.py`)
- Backup management (`backup.py`)
- Logging configuration (`logging_config.py`)

### 2. Integration Tests
Complete workflows tested end-to-end.

**Coverage:**
- Full vault lifecycle (create, load, save, modify)
- Import/export workflows
- Backup and restore workflows
- Settings persistence

### 3. Security Tests
Cryptographic and security-focused tests.

**Coverage:**
- Encryption/decryption correctness
- Key derivation function
- Vault integrity verification
- Password strength validation
- Sensitive data sanitization in logs

### 4. UI Tests
GUI component testing (when pytest-qt is available).

**Coverage:**
- Dialog interactions
- Main window functionality
- Settings persistence

### 5. Manual Tests
Human-performed tests for UX and edge cases.

**Coverage:**
- Visual verification
- Accessibility
- Cross-platform compatibility
- Performance with large vaults

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov

# Optional: Install pytest-qt for UI testing
pip install pytest-qt
```

### Run All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=pwick --cov-report=html
```

### Run Specific Test Files

```bash
# Unit tests only
pytest tests/test_vault.py

# Integration tests only
pytest tests/test_integration.py

# Configuration tests
pytest tests/test_config.py
```

### Run Specific Test Functions

```bash
# Run a specific test
pytest tests/test_vault.py::TestVault::test_create_vault

# Run tests matching a pattern
pytest -k "test_add"
```

---

## Unit Testing

### Vault Core Tests (`tests/test_vault.py`)

**Test Coverage:**
- `test_create_vault`: Vault creation with correct metadata
- `test_load_vault`: Loading and decrypting existing vault
- `test_wrong_password`: Authentication error on incorrect password
- `test_add_entry`: Adding password entries
- `test_add_note`: Adding note entries
- `test_update_entry`: Updating entry fields
- `test_update_note`: Updating note entries
- `test_delete_entry`: Deleting entries
- `test_save_and_load_with_entries`: Full save/load cycle
- `test_export_import`: Export and import workflows
- `test_integrity_verification`: File integrity checks
- `test_password_change_tracking`: Last password change timestamps
- `test_configurable_password_history`: Variable history limits

**Example:**
```python
def test_create_vault(self):
    vault_data = vault.create_vault(self.vault_path, self.master_password)
    self.assertIsNotNone(vault_data)
    self.assertEqual(vault_data['metadata']['version'], '2.0')
    self.assertTrue(os.path.exists(self.vault_path))
```

### Configuration Tests (`tests/test_config.py`)

**Test Coverage:**
- `test_default_settings`: Verify all default settings present
- `test_load_nonexistent_config`: Returns defaults when config missing
- `test_save_and_load_settings`: Settings persistence
- `test_settings_validation`: Range and type validation
- `test_settings_migration`: Backwards compatibility

### Backup Tests (`tests/test_backup.py`)

**Test Coverage:**
- `test_create_backup`: Backup file creation
- `test_list_backups`: Listing backup files
- `test_cleanup_old_backups`: Rotation of old backups
- `test_restore_backup`: Restoration from backup
- `test_auto_backup`: Automatic backup with settings

---

## Integration Testing

### Complete Workflow Tests (`tests/test_integration.py`)

**Test Coverage:**
- `test_complete_workflow`: Full lifecycle test
  1. Create new vault
  2. Add multiple entries (passwords and notes)
  3. Save vault
  4. Load vault
  5. Verify wrong password fails
  6. Update entries
  7. Delete entries
  8. Export vault
  9. Import vault
  10. Verify data integrity

**Example:**
```python
def test_complete_workflow(self):
    # Create vault
    vault_data = vault.create_vault(self.vault_path, self.master_password)

    # Add entries
    vault.add_entry(vault_data, 'GitHub', 'user@example.com', 'pass123')
    vault.add_note(vault_data, 'Shopping List', 'Milk, Bread, Eggs')

    # Save and reload
    vault.save_vault(self.vault_path, vault_data, self.master_password)
    loaded_vault = vault.load_vault(self.vault_path, self.master_password)

    # Verify
    self.assertEqual(len(loaded_vault['entries']), 2)
```

---

## Security Testing

### Cryptographic Tests

**Test Objectives:**
- Verify encryption produces different ciphertext for same plaintext (nonce randomness)
- Verify decryption recovers original plaintext
- Verify authentication tag prevents tampering
- Verify key derivation produces consistent keys
- Verify salt randomness

**Example Security Test:**
```python
def test_encryption_randomness(self):
    """Verify encryption produces different output each time (nonce randomness)."""
    key = AESGCM.generate_key(bit_length=256)
    plaintext = b"sensitive data"

    encrypted1 = _encrypt_data(plaintext, key)
    encrypted2 = _encrypt_data(plaintext, key)

    # Nonces should be different
    self.assertNotEqual(encrypted1['nonce'], encrypted2['nonce'])
    # Ciphertexts should be different
    self.assertNotEqual(encrypted1['ciphertext'], encrypted2['ciphertext'])
```

### Integrity Verification Tests

**Test Objectives:**
- Verify integrity hash computed correctly
- Verify tampering detected
- Verify backwards compatibility (vaults without hash)

**Example:**
```python
def test_integrity_verification(self):
    """Verify vault integrity checking detects tampering."""
    vault_data = vault.create_vault(self.vault_path, self.master_password)
    vault.save_vault(self.vault_path, vault_data, self.master_password)

    # Tamper with vault file
    with open(self.vault_path, 'r') as f:
        data = json.load(f)
    data['integrity_hash'] = "0" * 64  # Invalid hash
    with open(self.vault_path, 'w') as f:
        json.dump(data, f)

    # Should raise integrity error
    with self.assertRaises(vault.VaultIntegrityError):
        vault.load_vault(self.vault_path, self.master_password)
```

### Password Strength Tests

**Test Objectives:**
- Verify zxcvbn integration
- Verify weak password detection
- Verify strength thresholds

### Sensitive Data Sanitization Tests

**Test Objectives:**
- Verify passwords redacted from logs
- Verify master password never logged
- Verify log filter effectiveness

---

## Manual Testing

### Manual Test Checklist

#### Initial Setup
- [ ] Fresh install on clean system (Windows, Linux)
- [ ] Python version check (3.9+)
- [ ] All dependencies install correctly
- [ ] Application launches without errors

#### Core Functionality
- [ ] Create new vault with master password
- [ ] Master password strength validation works
- [ ] Vault file created at specified location
- [ ] Unlock vault with correct password
- [ ] Unlock fails with incorrect password
- [ ] Add new password entry
- [ ] Add new note entry
- [ ] Edit existing entry
- [ ] Delete entry with confirmation
- [ ] Copy password to clipboard
- [ ] Clipboard auto-clears after timeout
- [ ] Clipboard history shows last 30 items
- [ ] Search/filter entries works correctly

#### Security Features
- [ ] Auto-lock after inactivity works
- [ ] Manual lock clears sensitive data
- [ ] Password generator creates strong passwords
- [ ] Password strength meter shows accurate ratings
- [ ] Security audit detects duplicate passwords
- [ ] Security audit detects weak passwords
- [ ] Password history shows last N passwords
- [ ] Password expiration warnings appear correctly

#### Tag & Organization Features
- [ ] Add tags to entries
- [ ] Filter by tags
- [ ] Rename tags
- [ ] Delete tags
- [ ] Pin/unpin entries
- [ ] Pinned entries sort to top

#### Backup & Recovery
- [ ] Export vault to encrypted file
- [ ] Import vault from encrypted file
- [ ] Export to CSV works correctly
- [ ] Import from CSV works correctly
- [ ] Automatic backup creates backups
- [ ] Old backups cleaned up correctly
- [ ] Restore from backup works

#### Settings & Configuration
- [ ] All settings save correctly
- [ ] Settings persist across sessions
- [ ] Theme switching works (dark/light)
- [ ] Auto-lock timeout configurable
- [ ] Password generator settings work
- [ ] Backup settings work

#### System Integration
- [ ] System tray icon appears
- [ ] Minimize to tray works
- [ ] Double-click tray to restore
- [ ] Tray context menu works
- [ ] Application quits cleanly
- [ ] Keyboard shortcuts work correctly

#### Cross-Platform
- [ ] Test on Windows 10/11
- [ ] Test on Linux (Ubuntu, Fedora)
- [ ] Test on macOS (if supported)
- [ ] File paths work correctly on each OS
- [ ] Config directory created in correct location

#### Performance
- [ ] Application launches quickly (<2 seconds)
- [ ] Vault loads quickly (<1 second for small vaults)
- [ ] Search is responsive with 1000+ entries
- [ ] No memory leaks with extended use
- [ ] No UI freezing during operations

#### Edge Cases
- [ ] Handle very long passwords (>500 characters)
- [ ] Handle very long notes (>10000 characters)
- [ ] Handle many tags (>50 per entry)
- [ ] Handle large number of entries (>10000)
- [ ] Handle special characters in all fields
- [ ] Handle Unicode characters correctly
- [ ] Handle corrupted vault file gracefully
- [ ] Handle disk full errors gracefully
- [ ] Handle permission errors gracefully

---

## Code Coverage

### Coverage Goals

- **Overall:** >80% code coverage
- **Core (vault.py):** >95% coverage
- **Security functions:** 100% coverage
- **UI:** >60% coverage (harder to test)

### Generating Coverage Reports

```bash
# Run tests with coverage
pytest --cov=pwick --cov-report=html --cov-report=term

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Analysis

Focus on:
1. **Branch coverage:** All if/else paths tested
2. **Exception coverage:** All exception paths tested
3. **Edge cases:** Boundary conditions tested

---

## Continuous Integration

### GitHub Actions Workflow (Recommended)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install .[test]
    - name: Run tests
      run: pytest --cov=pwick --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## Security Testing Best Practices

### 1. Never Log Sensitive Data
- Always use log sanitization filter
- Test that passwords never appear in logs
- Test that master password never appears in logs

### 2. Test Encryption Thoroughly
- Test with various input sizes
- Test with special characters
- Test with Unicode
- Test encryption/decryption roundtrip
- Test that tampering is detected

### 3. Test Key Derivation
- Verify consistent key derivation
- Verify different salts produce different keys
- Verify key derivation parameters are correct

### 4. Test Backwards Compatibility
- Keep old vault files for regression testing
- Test migration from v1.x to v2.x
- Verify no data loss during migration

---

## Reporting Issues

If you discover a bug during testing:

1. **Check if already reported:** Search existing GitHub issues
2. **Create minimal reproduction:** Simplest steps to reproduce
3. **Include details:**
   - OS and version
   - Python version
   - pwick version
   - Exact error message
   - Steps to reproduce
4. **For security issues:** Email maintainer directly (do NOT create public issue)

---

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach recommended)
2. **Maintain coverage:** Don't decrease overall coverage
3. **Test edge cases:** Not just happy path
4. **Document tests:** Clear test names and docstrings
5. **Run full test suite:** Before submitting PR

---

**Last Updated:** November 2025
**Version:** 2.2.0
