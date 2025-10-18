# pwick 🛡️
**Version 1.0.0** - _A simple, secure, and 100% local password manager._

pwick is a cross-platform password manager built for users who demand absolute privacy. Your data **never** leaves your computer, is **never** sent to a server, and is **always** protected by strong, internal encryption.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)

---

## Philosophy: Your Data is Yours. Period.

In an age of constant cloud syncing and data breaches, pwick is intentionally different. We believe your most sensitive information—your passwords—should remain completely and totally under your control.

* **No Cloud:** There is no "sync" feature. There are no servers. Your vault is a single file on your local disk.
* **No Tracking:** The application includes no analytics, no tracking pixels, and no network "check-ins."
* **Total Privacy:** You are the only person who can access your data.

---

## Features

### Core Security
* 🔒 **100% Local-First:** Your vault is a single, encrypted file on your computer
* 🔑 **Strong Encryption:** AES-256-GCM authenticated encryption prevents data tampering
* 🛡️ **Argon2id Key Derivation:** Winner of the Password Hashing Competition, protects against brute-force attacks
  - Time cost: 3 iterations
  - Memory cost: 65536 KB (64 MB)
  - Parallelism: 1 thread
  - Unique 16-byte salt per vault
* 🔐 **Master Password Security:** Never stored on disk, exists only in memory when vault is unlocked
* 💾 **Encrypted Backups:** Export/import functionality for secure vault transfer between devices

### User Interface
* 💻 **Cross-Platform:** Works natively on Windows and Linux
* 🎨 **Dark Theme:** Black, grey, white, and red color scheme for comfortable viewing
* ⌨️ **Keyboard Shortcuts:** Ctrl+C (copy), Ctrl+N (new), Ctrl+E (edit), Delete, Ctrl+L (lock), Ctrl+F (find)
* 📋 **Clipboard Management:**
  - Auto-clear after 30 seconds for security
  - History panel showing last 30 copies
  - Daily refresh of clipboard history
* 🔄 **Password Tools:**
  - 20-character strong password generator
  - Show/hide toggle for password visibility
  - One-click copy to clipboard

### Entry Management
* ➕ **Create:** Add new password entries with title, username, password, and notes
* ✏️ **Edit:** Update existing entries with full history tracking
* 🗑️ **Delete:** Remove entries with confirmation dialog
* 🔍 **Search:** Quick find with Ctrl+F to focus entry list
* 🏷️ **Organization:** Each entry includes UUID, timestamps, and metadata

---

## Screenshots

### Welcome Screen
![Welcome Screen](docs/screenshots/welcome_screen.png)

### Entry Management
![Entry Dialog](docs/screenshots/entry_dialog.png)

The application features a dark theme with a clean, distraction-free interface designed for security and ease of use.

---

## Installation

### Quick Install (Recommended)

#### Windows
1. Download the repository or release package
2. Open Command Prompt in the pwick directory
3. Run the installation script:
   ```cmd
   install.bat
   ```
4. Follow the on-screen instructions
5. Run pwick from anywhere:
   ```cmd
   pwick
   ```

#### Linux / Mac
1. Download the repository or release package
2. Open terminal in the pwick directory
3. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
4. Choose user or system-wide installation
5. Run pwick from anywhere:
   ```bash
   pwick
   ```

### Manual Installation

#### Using pip (All Platforms)
```bash
# Install from source directory
pip install .

# Or for development (editable install)
pip install -e .
```

### Build From Source

If you prefer to build the project yourself without installing:

1.  Clone the repository:
    ```bash
    git clone https://github.com/orpheus497/pwick.git
    cd pwick
    ```

2.  Run the build script (Linux/Mac):
    ```bash
    chmod +x build.sh
    ./build.sh
    ```
    
    Or manually (Windows/Linux/Mac):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  Run the application:
    ```bash
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    python -m src.pwick
    ```

**Requirements:**
- Python 3.7 or higher
- Dependencies (installed automatically):
  - PyQt5 5.15.10 (GUI framework)
  - cryptography 41.0.7 (AES-256-GCM encryption)
  - argon2-cffi 23.1.0 (Argon2id key derivation)
  - pyperclip 1.8.2 (clipboard support)

---

## Uninstallation

### Using Uninstall Script

#### Windows
```cmd
uninstall.bat
```

#### Linux / Mac
```bash
chmod +x uninstall.sh
./uninstall.sh
```

### Manual Uninstallation
```bash
pip uninstall pwick
```

**Note:** Uninstalling pwick does NOT delete your vault files. They remain at their saved locations for safety.

---

## How to Use

### 1. First-Time Setup

When you first launch the application, you will be asked to create a new vault.

1.  Choose **"Create New Vault"**.
2.  Set your **Master Password**.

**⚠️ IMPORTANT: Your Master Password is the *only* key to your data. It is never stored by us and cannot be recovered. If you forget your Master Password, your data is lost forever. Write it down and store it somewhere safe.**

### 2. Daily Use

* Use your Master Password to unlock your vault.
* Add, edit, copy, or delete your password entries.
* **Copy passwords securely**: Click "Copy Password" or press `Ctrl+C` - the password is automatically cleared from your clipboard after 30 seconds for security.
* **Clipboard History**: View the last 30 copied passwords in the history panel. Double-click any item to copy it again. History automatically refreshes each new day.
* **Use keyboard shortcuts** for quick access:
  - `Ctrl+C`: Copy password
  - `Ctrl+N`: Add new entry
  - `Ctrl+E`: Edit entry
  - `Delete`: Delete entry
  - `Ctrl+L`: Lock vault
  - `Ctrl+F`: Focus entry list for quick navigation
* Lock the vault when you step away from your computer to keep it secure.

---

## Backup and Device Transfer

You can easily move your *entire* vault between devices without any cloud service.

### To Export (Backup)

1.  Unlock your vault.
2.  Navigate to `File > Export Encrypted Vault`.
3.  Choose a name and location to save your encrypted file (e.g., `my-pwick-vault.encrypted`).
4.  Securely copy this single file to a USB drive or other offline media.

This file contains all your data, but it remains fully encrypted by your Master Password.

### To Import (Transfer to New Device)

1.  Install pwick on your new computer.
2.  Copy your exported file (e.g., `my-pwick-vault.encrypted`) to the new device.
3.  On the application's welcome screen, choose **"Import Existing Vault"**.
4.  Select your file.
5.  Enter the **same Master Password** you used to create the vault.

Your vault will be decrypted and loaded locally on the new machine.

---

## Security Model

* **Encryption at Rest:** Your local vault file is fully encrypted using **AES-256-GCM** (Advanced Encryption Standard with Galois/Counter Mode), which provides both confidentiality and authenticity.
* **Key Derivation:** Your Master Password is run through **Argon2id** (winner of the Password Hashing Competition) to create the encryption key. This uses:
  - Time cost: 3 iterations
  - Memory cost: 65536 KB (64 MB)
  - Parallelism: 1 thread
  - Salt: 16 random bytes (unique per vault)
  
  These settings make brute-force attacks computationally expensive and memory-intensive.
* **No Plaintext:** Your Master Password is never stored on disk, not even in a hashed form. It is only held in memory when the vault is unlocked.

---

## Contributing

We welcome contributions! If you'd like to help improve pwick, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
