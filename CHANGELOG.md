# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Vault file integrity verification using SHA-256 hashing to detect corruption and tampering
- Password change tracking with `last_password_change` timestamp field in entries
- Configurable password history limit via settings (default: 5, range: 1-20)
- Password expiration tracking system with configurable expiration days (default: 90 days)
- Password expiration warning system with configurable warning period (default: 14 days)
- Automatic backup system with configurable frequency (daily, weekly, on_change)
- Automatic backup rotation keeping configurable number of recent backups (default: 5)
- Backup management module (backup.py) for creating, listing, and restoring backups
- Comprehensive logging system with rotating file handler and configurable log levels
- Sensitive data sanitization filter for logs preventing password leakage
- Logging configuration module (logging_config.py) for centralized logging setup
- Light theme support in addition to existing dark theme
- Theme management module (themes.py) for centralized theme handling
- New settings for password history limit, expiration tracking, auto-backup, logging, and sorting
- Settings validation for all new configuration options
- TESTING.md documentation with comprehensive testing procedures and guidelines
- Log file patterns and backup directory patterns added to .gitignore

### Changed
- Vault Entry TypedDict now includes `last_password_change` field for password age tracking
- Vault file format now includes `integrity_hash` field for file integrity verification
- Vault load function now verifies integrity hash when present (backwards compatible)
- Vault save function now computes and stores integrity hash
- Entry update function now updates `last_password_change` when password changes
- Entry migration function updated to handle v2.2 format with new fields
- Settings default dictionary expanded with new configuration options
- Settings validation function expanded to validate all new settings
- Configuration module updated to support 13 new settings for enhanced functionality
- Theme stylesheet extracted from main_window.py to themes.py module for better organization

### Fixed
- Vault integrity verification prevents use of corrupted or tampered vault files
- Password change timestamps enable accurate password age calculation
- Backup system prevents data loss from user forgetfulness or system failures

### Security
- Vault file integrity verification detects unauthorized modifications
- Logging system sanitizes sensitive data preventing password exposure in logs
- Password expiration tracking encourages regular password rotation
- Automatic backups reduce risk of data loss from corruption or accidents

### Documentation
- Created comprehensive TESTING.md with unit, integration, security, and manual testing procedures
- Updated SECURITY.md to reference correct dependency (PySide6 instead of PyQt5)
- Updated .gitignore to exclude log files, backup files, and development artifacts
- Enhanced code documentation with detailed docstrings in new modules

### Migration
- All vault format changes maintain backwards compatibility through migration functions
- Existing vaults load correctly and automatically migrate to new format on save
- New fields added to entries with sensible defaults (timestamps, empty lists, false booleans)
- Settings migration automatically adds new settings with defaults when loading old configs

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