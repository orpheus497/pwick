# pwick 🛡️
**Version 2.4.0** - _A simple, secure, and 100% local password manager._

Created by orpheus497.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-2.4.0-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

pwick is a cross-platform password manager that provides absolute privacy. Your data never leaves your computer, is never sent to a server, and is always protected by strong encryption.

## Philosophy

Your most sensitive information—your passwords and notes—remain completely under your control.

*   **No Cloud:** Your vault is a single file on your local disk.
*   **No Tracking:** No analytics, no tracking pixels, no network connections.
*   **Total Privacy:** You are the only person who can access your data.

---

## Features

### Security
*   **Encryption:** AES-256-GCM authenticated encryption with Argon2id key derivation.
*   **Vault Integrity:** SHA-256 hashing detects file corruption and tampering.
*   **Upgradable KDF:** Argon2id parameters are stored in the vault, allowing for security improvements over time.
*   **Master Password:** Never stored on disk, exists only in memory when unlocked.
*   **Encrypted Clipboard:** Passwords encrypted with a session-unique AES-256-GCM key before copying to the system clipboard to prevent snooping.
*   **Secure Clipboard History:** Clipboard history stores encrypted passwords, not plaintext.
*   **Auto-Clear Clipboard:** Clipboard is automatically cleared after 30 seconds.
*   **Auto-Lock:** Vault automatically locks after a configurable period of inactivity.
*   **Password Expiration:** Track password age with configurable expiration warnings.
*   **Password History:** Keep last N passwords per entry to prevent reuse.
*   **Security Audit:** Detect duplicate and weak passwords across entries.
*   **Automatic Backups:** Timestamped backups with configurable retention.
*   **Import/Export:** Encrypted backup functionality for vault transfer.

### Interface
*   **Cross-Platform:** Supports Windows, Linux, and macOS with platform-native features.
*   **Modern UI:** Choose between dark, light, or auto themes (auto matches your system theme) with a tabbed interface for managing passwords and notes.
*   **Command Palette:** Quick command launcher with fuzzy search (`Ctrl+K`) for fast access to all functions.
*   **Tag Management:** Organize entries with tags, featuring autocomplete and removable chips.
*   **Pinned Entries:** Pin important entries to keep them at the top of your list.
*   **Advanced Search:** Real-time text search combined with tag and pinned status filtering.
*   **Flexible Sorting:** Sort entries 6 ways (A-Z, Z-A, Date Created/Modified, Newest/Oldest).
*   **Tag Manager:** Centralized tag management with rename, merge, and delete operations.
*   **System Tray:** Minimizes to tray, runs in the background, and restores with a double-click.
*   **Keyboard Shortcuts:** A full set of keyboard shortcuts for quick access to all major functions.
*   **Password Generator:** Generates strong, customizable passwords.
*   **Password Strength Meter:** Visual feedback using zxcvbn algorithm.
*   **Enhanced Import:** Import from KeePass, Bitwarden (JSON/CSV), LastPass, 1Password, and generic CSV with auto-format detection.
*   **Backup Manager UI:** Visual backup browser with one-click restore, manual backup creation, and automatic cleanup.
*   **CSV Import/Export:** Import and export password entries from/to CSV files.
*   **Comprehensive Settings:** 7-tab settings dialog for fine-grained control.
*   **Application Logging:** Configurable logging with sensitive data sanitization.

---

## Screenshots

![Welcome Screen](docs/screenshots/welcome_screen.png)
![Entry Dialog](docs/screenshots/entry_dialog.png)

---

## Installation

### Standalone Executables (Recommended)

Build a single-file executable that doesn't require Python installation:

**Windows:**
```cmd
build_exe.bat
```

**Linux/macOS:**
```bash
./build_exe.sh
```

The executable will be created in the `dist/` folder. See [BUILD.md](BUILD.md) for detailed build instructions.

**Advantages:**
- No Python installation required
- Single executable file
- Faster startup time
- Easy distribution

### Quick Install (Python)

**Windows:**
```cmd
install.bat
```

**Linux/Mac:**
```bash
./install.sh
```

These scripts set up a local Python virtual environment and install all necessary dependencies. After installation, run pwick using the generated launcher script:

**Windows:**
```cmd
run_pwick.bat
```

**Linux/Mac:**
```bash
./run_pwick.sh
```

### Build From Source

```bash
# Clone repository
git clone https://github.com/orpheus497/pwick.git
cd pwick

# Automated build (sets up local venv and installs dependencies)
./build.sh

# Manual build (if you prefer to manage the venv yourself)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# Run
python -m pwick
```

**Requirements:** Python 3.9+, PySide6, cryptography, argon2-cffi, pyperclip, zxcvbn, tomli/tomli-w (all installed automatically by the setup scripts).

### Linux Additional Requirements

For clipboard functionality on Linux, you need `xclip` or `xsel` installed:

**Debian/Ubuntu:**
```bash
sudo apt install xclip
```

**Fedora/RHEL:**
```bash
sudo dnf install xclip
```

**Arch Linux:**
```bash
sudo pacman -S xclip
```

**Alternative (xsel):**
```bash
sudo apt install xsel  # Use xsel instead of xclip
```

**Note:** Users on Wayland-based systems may experience clipboard issues. If you encounter problems, please report them in the GitHub issues.

---

## Uninstallation

To remove the local pwick environment (virtual environment and launcher scripts):

**Windows:** `uninstall.bat`  
**Linux/Mac:** `./uninstall.sh`  

*Note: Your vault files are NOT deleted for safety. They remain at their saved locations.*

---

## Usage

### First-Time Setup
1.  Launch pwick using its launcher script (`run_pwick.sh` or `run_pwick.bat`).
2.  Choose "Create New Vault".
3.  Set your Master Password.

**⚠️ IMPORTANT:** Your Master Password cannot be recovered. If you forget it, your data is permanently inaccessible.

### Daily Use
*   Unlock vault with Master Password.
*   Use the "Passwords" and "Notes" tabs to manage your entries.
*   **Command Palette:** Press `Ctrl+K` to open the command palette for quick access to any function with fuzzy search.
*   **Search & Filter:** Use the search bar combined with tag and pinned filters to quickly find entries.
*   **Sorting:** Choose from 6 sorting modes to organize your entries (A-Z, Z-A, by date, etc.).
*   **Tags:** Add tags to entries for better organization; use the Tag Manager (Tools menu) for bulk operations.
*   **Pin Entries:** Mark frequently used entries as pinned to keep them at the top.
*   **Copy passwords:** Click "Copy Password" or press `Ctrl+C` (auto-clears after 30 seconds).
*   **Clipboard History:** View last 30 copies, double-click to reuse.
*   **Password Age:** See how old passwords are and receive expiration warnings.
*   **Security Audit:** Run periodic security audits (Tools menu) to find weak or duplicate passwords.
*   **Backup Manager:** Access visual backup browser (Tools menu) to view, restore, and manage vault backups.
*   **Import from Other Managers:** Use the Import Wizard (File menu) to migrate from KeePass, Bitwarden, LastPass, or 1Password.
*   **Settings:** Configure all features including auto theme detection via the comprehensive Settings dialog (Tools menu).
*   **System Tray:** Close the window to minimize to tray; double-click the tray icon to restore.
*   Lock the vault when idle, or let the auto-lock feature do it for you.

### Backup and Transfer
**Export:** Click "Export Vault" → Save encrypted file  
**Import:** Choose "Import Existing Vault" → Select file → Enter Master Password

---

## Acknowledgements

*   **Original Creator:** The design and original implementation of this project were done by orpheus497.
*   **Keep a Changelog:** For the standardized changelog format.
*   **Semantic Versioning:** For clear versioning guidelines.
*   **PySide6** (LGPL v3): For the robust and flexible Qt6 GUI framework.
*   **cryptography** (Apache 2.0 / BSD): For cryptographic primitives and secure encryption.
*   **argon2-cffi** (MIT): For strong Argon2id key derivation functions.
*   **pyperclip** (BSD 3-Clause): For cross-platform clipboard operations.
*   **zxcvbn** (MIT): For accurate password strength estimation algorithm.
*   **tomli** / **tomli-w** (MIT): For TOML configuration file support.
*   **PyInstaller** (GPL v2 + exception): For standalone executable creation.
*   **pytest** / **pytest-qt** (MIT): For comprehensive testing framework.

---

## License

MIT License. See `LICENSE` file for details.
