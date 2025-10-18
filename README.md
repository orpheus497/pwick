# pwick 🛡️
_A simple, secure, and 100% local password manager._

pwick is a cross-platform password manager built for users who demand absolute privacy. Your data **never** leaves your computer, is **never** sent to a server, and is **always** protected by strong, internal encryption.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)

---

## Philosophy: Your Data is Yours. Period.

In an age of constant cloud syncing and data breaches, pwick is intentionally different. We believe your most sensitive information—your passwords—should remain completely and totally under your control.

* **No Cloud:** There is no "sync" feature. There are no servers. Your vault is a single file on your local disk.
* **No Tracking:** The application includes no analytics, no tracking pixels, and no network "check-ins."
* **Total Privacy:** You are the only person who can access your data.

---

## Features

* 🔒 **100% Local-First:** Your vault is a single, encrypted file on your computer.
* 🔑 **Strong Encryption:** Your entire vault is encrypted using **AES-256-GCM** (authenticated encryption) with a key derived from your Master Password using **Argon2id** key derivation function.
* 💻 **Cross-Platform:** Works natively on both **Windows** and **Linux**.
* 🔄 **Easy Backup & Transfer:** Securely export your *entire* encrypted vault to a single file. Move it to a new device via a USB drive (or any other method) and import it seamlessly.
* ✨ **Simple Interface:** A clean, no-nonsense UI with dark theme focused on one thing: managing your passwords securely.

---

## Installation

### From Releases

This is the easiest way to get started.

1.  Go to the [**Releases Page**](httpsa://github.com/YourUsername/pwick/releases).
2.  Download the latest file for your operating system:
    * **Windows:** `pwick-v1.0.exe` (or `.msi`)
    * **Linux:** `pwick-v1.0.AppImage` (or `.deb`/`.rpm`)
3.  (For Linux .AppImage) Make the file executable:
    ```bash
    chmod +x pwick-v1.0.AppImage
    ```
4.  Run the application.

### Build From Source

If you prefer to build the project yourself:

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
- Dependencies (installed automatically by build script):
  - PyQt5 (GUI framework)
  - cryptography (AES-256-GCM encryption)
  - argon2-cffi (Argon2id key derivation)
  - pyperclip (clipboard support)

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
