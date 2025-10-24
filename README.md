# pwick 🛡️
**Version 1.0.1** - _A simple, secure, and 100% local password manager._

Created by orpheus497.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.1-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)

pwick is a cross-platform password manager that provides absolute privacy. Your data never leaves your computer, is never sent to a server, and is always protected by strong encryption.

## Philosophy

Your most sensitive information—your passwords and notes—remain completely under your control.

*   **No Cloud:** Your vault is a single file on your local disk.
*   **No Tracking:** No analytics, no tracking pixels, no network connections.
*   **Total Privacy:** You are the only person who can access your data.

---

## Features

### Security
*   **Encryption:** AES-256-GCM authenticated encryption with Argon2id key derivation
    *   Time cost: 3 iterations, Memory cost: 64 MB, Parallelism: 1 thread
    *   Unique 16-byte salt per vault
    *   Prevents brute-force, dictionary, and rainbow table attacks
*   **Master Password:** Never stored on disk, exists only in memory when unlocked
*   **Encrypted Clipboard:** Passwords encrypted with AES-256-GCM before copying to system clipboard
    *   Prevents OS telemetry and clipboard snooping
    *   Session-unique encryption key
    *   Auto-clears after 30 seconds
*   **Import/Export:** Encrypted backup functionality for vault transfer

### Interface
*   **Cross-Platform:** Supports Windows and Linux.
*   **Modern UI:** Features a dark theme (black, grey, white, and red color scheme) and a tabbed interface for organized management of passwords and notes.
*   **System Tray:** Minimizes to tray, runs in the background, and restores with a double-click.
*   **Keyboard Shortcuts:**
    *   `Ctrl+C`: Copies password
    *   `Ctrl+N`: Adds a new password entry
    *   `Ctrl+Shift+N`: Adds a new note entry
    *   `Ctrl+E`: Edits a password entry
    *   `Ctrl+Shift+E`: Saves a note entry
    *   `Delete`: Deletes a password entry
    *   `Ctrl+Shift+Delete`: Deletes a note entry
    *   `Ctrl+L`: Locks the vault
    *   `Ctrl+F`: Focuses/finds an entry
*   **Clipboard History:** A panel shows the last 30 copied items (refreshes daily).
*   **Password Generator:** Generates 20-character strong passwords with a show/hide toggle.
*   **Entry Management:** Creates, edits, and deletes entries with title, username, password, and notes.
*   **Notes Management:** Dedicated tab for creating, editing, and managing secure notes.
*   **CSV Import:** Imports password entries from CSV files, handling various field mappings.

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
chmod +x install.sh
./install.sh
```

These scripts set up a local Python virtual environment and install all necessary dependencies. After installation, run pwick using the generated launcher script:

**Windows:**
```cmd
.\run_pwick.bat
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
chmod +x build.sh
./build.sh

# Manual build (if you prefer to manage the venv yourself)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install .

# Run
python -m pwick
```

**Requirements:** Python 3.7+, PyQt5, cryptography, argon2-cffi, pyperclip (all installed automatically by the setup scripts).

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
*   Use the "Passwords" tab to add, edit, copy, or delete password entries.
*   Use the "Notes" tab to create, edit, or delete secure notes.
*   **Copy passwords:** Click "Copy Password" or press `Ctrl+C` (auto-clears after 30 seconds).
*   **Clipboard History:** View last 30 copies, double-click to reuse (refreshes daily).
*   **System Tray:** Close the window to minimize to tray; double-click the tray icon to restore.
*   Lock the vault when idle.

### Backup and Transfer
**Export:** File > Export Encrypted Vault → Save encrypted file  
**Import:** Choose "Import Existing Vault" → Select file → Enter Master Password

---

## Security

*   **Encryption:** AES-256-GCM authenticated encryption.
*   **Key Derivation:** Argon2id (3 iterations, 64 MB memory, unique salt per vault).
*   **Master Password:** Never stored on disk.
*   **Encrypted Clipboard:** Passwords encrypted before copying (prevents telemetry/snooping).
*   **No Network:** Zero external connections, complete local-first architecture.

---

## Acknowledgements

*   **Keep a Changelog:** For the standardized changelog format.
*   **Semantic Versioning:** For clear versioning guidelines.
*   **PyQt5:** For the robust and flexible GUI framework.
*   **cryptography:** For cryptographic primitives.
*   **argon2-cffi:** For strong key derivation functions.
*   **pyperclip:** For cross-platform clipboard operations.

---

## License

MIT License. See `LICENSE` file for details.