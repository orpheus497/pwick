# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-18

### Added - Initial Release
- Complete local-first password manager implementation
- Core vault functionality with strong encryption:
  - Argon2id key derivation function (time_cost=3, memory_cost=65536 KB, parallelism=1)
  - AES-256-GCM authenticated encryption
  - JSON-based vault format with metadata and entries
  - Secure random salt generation (16 bytes per vault)
- Entry management features:
  - Create, read, update, and delete password entries
  - Each entry includes: title, username, password, notes, timestamps
  - UUID-based entry identification
- PyQt5-based desktop GUI with dark theme (black/grey/white/red color scheme):
  - Welcome screen with options to create, import, or open vault
  - Master password dialogs with confirmation for new vaults
  - Main window with entry list and detail views
  - Add/Edit entry dialogs with password generation
  - Password visibility toggle in entry dialogs
  - Strong password generator (20 characters, mixed alphanumeric and symbols)
  - Copy password to clipboard functionality with auto-clear after 30 seconds
  - Clipboard history panel showing last 30 copied passwords (refreshes daily)
  - Double-click clipboard history items to copy again
  - Keyboard shortcuts for common actions (Copy: Ctrl+C, New: Ctrl+N, Edit: Ctrl+E, Delete: Del, Lock: Ctrl+L, Find: Ctrl+F)
  - Lock vault feature to secure application when idle
- Vault import/export functionality:
  - Export entire vault to encrypted backup file
  - Import vault from backup to new location
  - Cross-device transfer support via encrypted files
- Cross-platform support:
  - Windows and Linux compatibility
  - Installation scripts for both platforms (install.bat, install.sh)
  - Uninstallation scripts (uninstall.bat, uninstall.sh)
- Packaging and distribution:
  - setup.py for pip installation
  - pyproject.toml for modern Python packaging
  - Entry points for command-line execution
  - MANIFEST.in for package data
- Build and development tools:
  - POSIX-compliant build.sh script for automated setup
  - Virtual environment management
  - Dependency installation automation
- Testing infrastructure:
  - Unit tests for core vault operations (8 tests)
  - Integration tests for complete workflows
  - Tests for encryption/decryption
  - Tests for entry CRUD operations
  - Tests for import/export functionality
- Documentation:
  - Comprehensive README with installation, usage, and uninstallation instructions
  - SECURITY.md with detailed security model and threat analysis
  - TESTING.md with comprehensive testing procedures
  - QUICKREF.md with quick reference guide and keyboard shortcuts
  - CHANGELOG.md following Keep a Changelog format
  - docs/ENHANCED_FEATURES.md for clipboard and keyboard features
  - docs/CLIPBOARD_HISTORY.md for clipboard history documentation
  - docs/IMPLEMENTATION_SUMMARY.md for technical details

### Security
- Master password never stored on disk
- Strong key derivation prevents brute-force attacks
- Authenticated encryption prevents tampering
- No network connections or external API calls
- Complete local-first architecture ensures data privacy
- Clipboard auto-clear after 30 seconds
- Daily refresh of clipboard history for security

### Fixed
- Timezone-aware datetime handling (no deprecation warnings)
- Proper error handling for vault authentication failures
- Secure file operations with proper permissions
