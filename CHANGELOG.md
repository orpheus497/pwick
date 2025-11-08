# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Missing QComboBox import in main_window.py preventing application startup
- Unused QFlowLayout import in entry_dialog.py
- Version number inconsistency across package files synchronized to 2.4.0
- Python 3.9 compatibility issue with modern type hints (added `from __future__ import annotations`)
- macOS configuration directory now uses standard `~/Library/Application Support/pwick/` instead of Linux-style `~/.config/`
- Clipboard operations now include comprehensive error handling with user-friendly messages
- Install scripts now dynamically read version from VERSION file instead of hardcoded strings

### Added
- **Backup Manager UI**: Visual backup browser with list view, one-click restore, manual backup creation, and automatic cleanup
- **System Theme Auto-Detection**: Automatic theme matching with OS dark/light mode on Windows, macOS, and Linux
- **Enhanced Import System**: Support for importing from KeePass, Bitwarden (JSON/CSV), LastPass, and 1Password with automatic format detection
- **Import Wizard Dialog**: User-friendly import wizard with file browser, format auto-detection, and detailed progress reporting
- **Command Palette**: VS Code-style quick command launcher with fuzzy search accessible via `Ctrl+K`
- **PyInstaller Build Scripts**: Cross-platform scripts (`build_exe.sh`, `build_exe.bat`) for creating standalone executables
- **UI Test Suite**: Comprehensive UI tests using pytest-qt covering all dialogs and widgets (test_ui_widgets.py)
- **Importer Tests**: Full test coverage for all import formats and error handling (test_importers.py)
- **System Theme Tests**: Complete test suite for cross-platform theme detection (test_system_theme.py)
- **Auto Theme Setting**: "Auto" option in settings dialog theme dropdown for automatic system theme matching
- **BUILD.md Documentation**: Comprehensive build documentation with troubleshooting and customization guides
- Input length validation for all text fields to prevent memory exhaustion attacks
- Maximum length constraints: title (256), username (256), password (1024), notes (10,000), tags (50 chars, 50 max)
- Character counter for notes field with color-coded visual feedback
- Tag length and count validation with user-friendly error messages
- Comprehensive test suite for configuration module (test_config.py)
- Comprehensive test suite for backup module (test_backup.py)
- Comprehensive test suite for logging module (test_logging.py)
- Belt-and-suspenders validation in entry save logic
- Error handling for clipboard operations with platform-specific installation instructions
- Linux clipboard dependency documentation in README (xclip/xsel requirements)
- macOS officially supported and documented (updated platform badge)
- Safe clipboard copy wrapper method with automatic error recovery

### Changed
- **Theme System**: Extended to support 'auto' mode in addition to 'dark' and 'light'
- **README**: Updated with standalone executable instructions, new features documentation, and enhanced usage guide
- **pyproject.toml**: Added optional dependencies for testing (pytest-qt, pytest-cov) and building (pyinstaller)
- **Settings Dialog**: Enhanced theme dropdown with Auto option and improved help text
- **Main Window**: Integrated Backup Manager, Import Wizard, and Command Palette with menu items and keyboard shortcuts
- Version updated from 2.3.0 to 2.4.0 across all files
- Platform support badge updated to include macOS (Windows | Linux | macOS)
- Configuration directory structure now platform-aware with proper macOS support
- Install scripts improved with dynamic version reading for maintainability
- Clipboard error messages provide actionable platform-specific installation commands

### Security
- Input validation prevents potential memory exhaustion attacks via oversized field data
- Character counters provide user feedback before hitting limits
- Validation occurs at UI level (setMaxLength) and business logic level (save validation)
- Clipboard operations fail gracefully without exposing sensitive data
- Import validation ensures malformed CSV/JSON files don't crash the application
- Backup restore operation creates safety backup before overwriting current vault

### Documentation
- Added BUILD.md with comprehensive standalone executable build instructions
- Added Linux clipboard requirements section to README
- Updated README with all new features (Backup Manager, Import Wizard, Command Palette, Auto Theme)
- Updated platform badge to include macOS
- Improved installation documentation with standalone executable section
- Added platform-specific requirements documentation
- Added Wayland compatibility notes for Linux users
- Enhanced acknowledgements section with PyInstaller and pytest credits

## [2.3.0] - 2025-11-08

### Fixed
- Critical import error causing application crash at startup (QComboBox missing from imports)
- Code hygiene issue with unused QFlowLayout import

### Added
- Comprehensive input validation across all entry fields
- Test coverage for configuration management (30+ test cases)
- Test coverage for backup functionality (25+ test cases)
- Test coverage for logging system (20+ test cases)

### Changed
- Version bumped from 2.2.0 to 2.3.0
- Entry dialog now enforces maximum field lengths at UI and validation layers
- Notes field displays live character counter with color coding

### Security
- Input validation system prevents memory exhaustion attacks
- Field length limits enforce reasonable data boundaries
- Dual-layer validation (UI + business logic) for defense in depth

## [2.2.0] - 2025-11-08

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
- Logging integration in main window for vault operations (create, open, import, export, lock)
- Theme switching on application startup based on user settings
- Integrity error handling with user-friendly error messages
- New settings for password history limit, expiration tracking, auto-backup, logging, and sorting
- Settings validation for all new configuration options
- TESTING.md documentation with comprehensive testing procedures and guidelines
- Log file patterns and backup directory patterns added to .gitignore
- Tag management UI in entry dialog with autocomplete and removable tag chips
- Pin checkbox in entry dialog for marking entries as favorites
- Password age display in entry dialog showing time since last password change
- Visual pin indicator (📌 emoji) for pinned entries in entry lists
- Tag display in entry lists showing all tags for each entry
- Automatic sorting with pinned entries at the top of lists
- Tag Manager dialog for centralized tag management (rename, merge, delete tags)
- Tag Manager accessible from Tools menu
- Password Management tab in Settings dialog for history and expiration settings
- Backup tab in Settings dialog for auto-backup configuration
- Logging tab in Settings dialog for log level and file size configuration
- Theme selection in Appearance tab of Settings dialog (Dark/Light)
- Backup location browser in Settings dialog for custom backup paths
- Entry sorting options with 6 modes (A-Z, Z-A, Date Created/Modified Newest/Oldest)
- Sort dropdown in password list interface for user-selectable sorting
- Advanced filtering by pinned status (All, Pinned Only, Unpinned Only)
- Advanced filtering by tag with dynamic tag dropdown populated from vault
- Combined filtering supporting simultaneous text search, pinned status, and tag filtering
- Tag filter dropdown automatically updates when tags are added, renamed, merged, or deleted

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
- Application startup now initializes logging system before creating UI
- Application startup now loads and applies theme from user settings
- Main window imports logging_config and themes modules
- CSV export function verified present and working (not a bug as initially assessed)
- Entry dialog (entry_dialog.py) completely rewritten with tag management and pin functionality
- Entry dialog now accepts `all_tags` parameter for tag autocomplete
- Entry dialog now returns tags and pinned status in result data
- Main window `_add_password_entry()` now passes tags and pinned to vault
- Main window `_edit_password_entry()` now passes tags and pinned to vault
- Main window `_refresh_lists()` now shows pin indicators and tag displays
- Main window entry lists now sort pinned entries at the top automatically
- Settings dialog now has 7 tabs instead of 4 (added Password Management, Backup, Logging)
- Settings dialog Appearance tab now allows theme switching (Dark/Light)
- Settings dialog now includes backup location browser for custom backup paths
- Settings dialog expanded from 355 lines to 560+ lines with new functionality
- Main window password list UI now includes sorting and filtering controls
- Entry list sorting now configurable with 6 different sorting modes
- _refresh_lists() method enhanced with dynamic sorting based on user selection
- _filter_lists() method enhanced with pinned status and tag filtering
- _populate_tag_filter() method added to dynamically populate tag dropdown
- Filtering now supports combining text search, pinned status, and tag selection

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