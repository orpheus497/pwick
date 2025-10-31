# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2025-10-31

### Added
- Configuration system with TOML-based settings file for user preferences
- Settings dialog with tabbed interface (General, Password Generator, Security, Appearance)
- Password strength validation for master password with visual feedback and minimum requirements
- Password strength meter widget using zxcvbn algorithm for accurate strength estimation
- Security audit feature detecting duplicate passwords across entries
- Security audit feature detecting weak passwords that should be upgraded
- Password history tracking (last 5 passwords per entry) with timestamp recording
- Password history viewer dialog with secure copy functionality
- Tagging system for organizing entries (data structure support)
- Favorites/pinned entries feature (data structure support)
- Backwards compatibility migration system for vault entries from v1.x to v2.x format
- New config module (config.py) for settings management with OS-appropriate paths
- Password strength widget (reusable component) with color-coded visual feedback
- Settings dialog widget with comprehensive preference management
- Security audit dialog widget with duplicate and weak password detection
- Password history dialog widget for viewing and copying historical passwords

### Changed
- **BREAKING:** Minimum Python version increased from 3.7 to 3.9 for security and modern features
- Clipboard history security model clarified: passwords stored in-memory only, cleared on lock/quit
- Entry data structure extended with tags, pinned status, and password history fields
- Master password dialog now includes strength meter and validation in creation mode
- Install scripts (install.sh, install.bat) now reference Python 3.9+ requirement
- README.md updated to reflect Python 3.9+ requirement and new dependencies
- STATUS.md comprehensively updated to reflect v2.0.0 status and features
- Vault entry structure now includes automatic migration for backwards compatibility

### Fixed
- **CRITICAL:** Clipboard history encryption implementation (was storing plaintext in memory incorrectly)
- Duplicate instance variable initialization in MainWindow class causing maintenance issues
- Incorrect run command in build.sh (was using `src.pwick` instead of `pwick`)
- Missing requirements.txt reference in install.sh (removed, using pyproject.toml)
- Empty __init__.py files in ui and ui/widgets modules (now have proper docstrings and imports)
- Outdated version information in STATUS.md

### Dependencies
- Added zxcvbn (≥4.4.28) for password strength estimation
- Added tomli (≥2.0.0, Python <3.11 only) for TOML config file reading
- Added tomli-w (≥1.0.0) for TOML config file writing

### Security
- Password strength validation prevents weak master passwords that would undermine encryption
- Security audit tools help users identify and fix password reuse and weak passwords
- Clipboard history memory model clarified and properly documented
- Password history encrypted at rest within vault file

## [1.0.1] - 2025-10-24

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
- PyQt5 desktop GUI with dark theme
- System tray integration
- Encrypted clipboard feature
- Clipboard history panel
- Keyboard shortcuts
- Vault import/export
- Cross-platform installation scripts
- Uninstallation scripts that preserve vault files
- Python package setup with pip installation support
- Command-line entry points
- Comprehensive test suite

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