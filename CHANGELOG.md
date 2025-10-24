# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1]

### Changed
- Modified installation scripts (install.sh, install.bat) to set up a local virtual environment instead of system-wide installation.
- Updated uninstallation scripts (uninstall.sh, uninstall.bat) to remove the local virtual environment.
- Refactored main UI to use a tabbed interface, separating "Passwords" and "Notes" sections.
- Renamed password-related UI methods and buttons for clarity (e.g., `_add_entry` to `_add_password_entry`).
- Modified vault entry structure to include an `entry_type` field (e.g., 'password', 'note').
- Updated `_refresh_entry_list` and `_find_entry` to handle different entry types.
- Adjusted keyboard shortcuts to include new note management actions and reflect renamed password actions.
- Improved CSV import to capture all fields and append unmapped data to notes.

### Added
- CSV import functionality for password entries.
- Dedicated "Notes" tab with features to add, edit, save, and delete notes.
- New methods for note management: `_add_note_entry`, `_on_note_selected`, `_save_note_entry`, `_delete_note_entry`.

## [1.0.0] - 2025-10-18

### Added
- Complete local-first password manager with strong encryption
- AES-256-GCM authenticated encryption with Argon2id key derivation
  - Time cost: 3 iterations, Memory: 64 MB, Parallelism: 1 thread
  - Unique 16-byte salt per vault
- PyQt5 desktop GUI with dark theme (black/grey/white/red)
  - Welcome screen (create/import/open vault)
  - Entry management (add/edit/delete with title, username, password, notes)
  - Password generator (20 characters, cryptographically secure)
  - Password visibility toggle
- System tray integration
  - Minimize to tray and run in background
  - Double-click tray icon to show/hide
  - Right-click menu (show/lock/quit)
  - Close button minimizes instead of quitting
- Encrypted clipboard feature
  - AES-256-GCM encryption before copying to system clipboard
  - Session-unique encryption key
  - Prevents OS telemetry and clipboard snooping
  - Auto-clear after 30 seconds
- Clipboard history panel
  - Shows last 30 copied passwords
  - Double-click to copy again
  - Automatically refreshes each new day
- Keyboard shortcuts
  - Ctrl+C: Copy password
  - Ctrl+N: New entry
  - Ctrl+E: Edit entry
  - Delete: Delete entry
  - Ctrl+L: Lock vault
  - Ctrl+F: Focus/find entry
- Vault import/export for encrypted backups and device transfer
- Cross-platform installation scripts (Windows: install.bat, Linux/Mac: install.sh)
- Uninstallation scripts that preserve vault files
- Python package setup (setup.py, pyproject.toml) with pip installation support
- Command-line entry points (`pwick` command)
- Comprehensive test suite (8 unit tests + integration tests)

### Security
- Master password never stored on disk
- Strong key derivation prevents brute-force attacks
- Authenticated encryption prevents tampering
- No network connections or external API calls
- Encrypted clipboard prevents telemetry
- Session-unique encryption keys
- Daily clipboard history refresh

### Documentation
- README with installation, usage, and security details
- CHANGELOG following Keep a Changelog format
- SECURITY policy and threat model
- TESTING procedures
- QUICKREF with keyboard shortcuts
- Comprehensive inline code documentation
