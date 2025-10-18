# pwick Quick Reference

## Command Line Usage

### Start the Application
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run
python -m src.pwick
```

### Run Tests
```bash
# Unit tests
python -m unittest tests.test_vault -v

# Integration test
python tests/test_integration.py
```

## Keyboard Shortcuts

Currently, pwick uses standard Qt shortcuts:
- `Enter` - Confirm dialog/action
- `Esc` - Cancel dialog
- `Tab` - Navigate between fields
- `Ctrl+C` / `Cmd+C` - Copy (when text is selected)

## File Formats

### Vault File (.vault)
- **Format**: JSON with encrypted data
- **Encryption**: AES-256-GCM
- **Key Derivation**: Argon2id
- **Location**: User-specified (recommended: keep in Documents or secure location)

### Encrypted Export (.encrypted)
- **Format**: Same as .vault file
- **Purpose**: Backup and transfer between devices
- **Usage**: Import via "Import Existing Vault" option

## Security Best Practices

### Master Password
- **Length**: Minimum 12 characters recommended
- **Complexity**: Mix uppercase, lowercase, numbers, symbols
- **Storage**: Write it down and keep in a secure physical location
- **Recovery**: IMPOSSIBLE - there is no password recovery mechanism

### Vault File
- **Backup**: Regularly export your vault to a .encrypted file
- **Storage**: Keep on encrypted drives or secure cloud storage (file is already encrypted)
- **Permissions**: On Linux/Mac, use `chmod 600 vault.vault` for extra security

### Usage Habits
- Always lock the vault when stepping away
- Don't leave the application running unattended
- Close the application when not in use
- Use the password generator for new accounts
- Update passwords periodically

## Troubleshooting

### Cannot Open Vault
**Problem**: "Failed to decrypt vault" error  
**Solution**: 
- Verify you're using the correct master password
- Check if vault file is corrupted (restore from backup)
- Ensure file wasn't modified by another program

### Application Won't Start
**Problem**: Application crashes on startup  
**Solution**:
- Verify Python 3.7+ is installed
- Rebuild virtual environment: `rm -rf venv && ./build.sh`
- Check if Qt dependencies are installed

### Password Not Copying
**Problem**: "Copy Password" doesn't work  
**Solution**:
- Verify clipboard access (pyperclip may need xclip/xsel on Linux)
- On Linux: `sudo apt-get install xclip`
- Try manually selecting and copying text

### Import Fails
**Problem**: Cannot import exported vault  
**Solution**:
- Verify the file is not corrupted
- Ensure you're using the same master password
- Check file permissions (should be readable)

## File Locations

### Default Locations (User Preference)
- **Vault File**: Anywhere user chooses (`.vault` extension recommended)
- **Exported Backups**: Anywhere user chooses (`.encrypted` extension recommended)
- **Virtual Environment**: `./venv/` (in project directory)

### Project Structure
```
pwick/
├── src/
│   └── pwick/
│       ├── __init__.py      # Package initialization
│       ├── __main__.py      # Entry point
│       ├── vault.py         # Core encryption/vault logic
│       └── ui.py            # PyQt5 GUI
├── tests/
│   ├── test_vault.py        # Unit tests
│   └── test_integration.py  # Integration tests
├── docs/
│   └── screenshots/         # UI screenshots
├── requirements.txt         # Python dependencies
├── build.sh                 # Build script
├── README.md               # Main documentation
├── CHANGELOG.md            # Version history
├── TESTING.md              # Testing guide
├── LICENSE                 # MIT License
└── .gitignore             # Git ignore rules
```

## API Reference (For Developers)

### Core Vault Functions

```python
from pwick import vault

# Create new vault
vault_data = vault.create_vault(path, master_password)

# Load existing vault
vault_data = vault.load_vault(path, master_password)

# Save vault
vault.save_vault(path, vault_data, master_password)

# Add entry
entry_id = vault.add_entry(vault_data, title, username, password, notes)

# Update entry
success = vault.update_entry(vault_data, entry_id, title=new_title, ...)

# Delete entry
success = vault.delete_entry(vault_data, entry_id)

# Export vault
vault.export_encrypted(source_path, target_path, master_password)

# Import vault
vault_data = vault.import_encrypted(source_path, target_path, master_password)
```

### Vault Data Structure

```python
{
    'metadata': {
        'version': '1.0',
        'created_at': '2025-10-18T00:00:00+00:00'
    },
    'entries': [
        {
            'id': 'uuid-string',
            'title': 'Entry Title',
            'username': 'username',
            'password': 'password',
            'notes': 'optional notes',
            'created_at': '2025-10-18T00:00:00+00:00',
            'updated_at': '2025-10-18T00:00:00+00:00'
        }
    ]
}
```

## Version Information

- **Current Version**: 1.0.0
- **Python**: 3.7+
- **License**: MIT
- **Repository**: https://github.com/orpheus497/pwick

## Getting Help

- **Issues**: Open an issue on GitHub
- **Documentation**: See README.md and TESTING.md
- **Contributing**: See README.md Contributing section
