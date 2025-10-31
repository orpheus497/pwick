# pwick 🛡️
**Version 2.1.0** - _A simple, secure, and 100% local password manager._

Created by orpheus497.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-2.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
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
*   **Upgradable KDF:** Argon2id parameters are stored in the vault, allowing for security improvements over time.
*   **Master Password:** Never stored on disk, exists only in memory when unlocked.
*   **Encrypted Clipboard:** Passwords encrypted with a session-unique AES-256-GCM key before copying to the system clipboard to prevent snooping.
*   **Secure Clipboard History:** Clipboard history stores encrypted passwords, not plaintext.
*   **Auto-Clear Clipboard:** Clipboard is automatically cleared after 30 seconds.
*   **Auto-Lock:** Vault automatically locks after a configurable period of inactivity.
*   **Import/Export:** Encrypted backup functionality for vault transfer.

### Interface
*   **Cross-Platform:** Supports Windows and Linux.
*   **Modern UI:** Dark theme and a tabbed interface for managing passwords and notes.
*   **Search:** Filter your passwords and notes with a real-time search bar.
*   **System Tray:** Minimizes to tray, runs in the background, and restores with a double-click.
*   **Keyboard Shortcuts:** A full set of keyboard shortcuts for quick access to all major functions.
*   **Password Generator:** Generates strong, 20-character passwords.
*   **CSV Import:** Import password entries from CSV files.

---

## Screenshots

![Welcome Screen](docs/screenshots/welcome_screen.png)
![Entry Dialog](docs/screenshots/entry_dialog.png)

---

## Installation

### Quick Install

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
*   Use the search bar to quickly find what you need.
*   **Copy passwords:** Click "Copy Password" or press `Ctrl+C` (auto-clears after 30 seconds).
*   **Clipboard History:** View last 30 copies, double-click to reuse.
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

---

## License

MIT License. See `LICENSE` file for details.
