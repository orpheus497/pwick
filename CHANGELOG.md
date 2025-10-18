# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
  - Keyboard shortcuts for common actions (Copy: Ctrl+C, New: Ctrl+N, Edit: Ctrl+E, Delete: Del, Lock: Ctrl+L, Find: Ctrl+F)
  - Lock vault feature to secure application when idle
- Vault import/export functionality:
  - Export entire vault to encrypted backup file
  - Import vault from backup to new location
  - Cross-device transfer support via encrypted files
- Build and development tools:
  - POSIX-compliant build.sh script for automated setup
  - Virtual environment management
  - Dependency installation automation
- Testing infrastructure:
  - Unit tests for core vault operations
  - Tests for encryption/decryption
  - Tests for entry CRUD operations
  - Tests for import/export functionality
- Documentation:
  - Comprehensive README with build instructions
  - Security model documentation
  - Usage instructions for daily operations
  - Backup and transfer procedures
  - CHANGELOG following Keep a Changelog format

### Security
- Master password never stored on disk
- Strong key derivation prevents brute-force attacks
- Authenticated encryption prevents tampering
- No network connections or external API calls
- Complete local-first architecture ensures data privacy
