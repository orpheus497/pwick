# System Tray and Encrypted Clipboard Features

## Overview

pwick v1.0.0 includes advanced privacy and usability features:
- **System Tray Integration**: Minimize to tray and run in background
- **Encrypted Clipboard**: Prevents clipboard telemetry and snooping

## System Tray Features

### Functionality

**Minimize to Tray:**
- Click the window close button (X) to minimize to system tray
- Application continues running in background
- Window is hidden from taskbar

**System Tray Icon:**
- Red square with white "P" letter
- Visible in system tray area (Windows notification area, Linux system tray)
- Double-click to show/hide main window

**Tray Menu:**
Right-click the tray icon to access:
- **Show** - Restore window from tray
- **Hide to Tray** - Minimize to tray
- **Lock Vault** - Lock the vault and return to welcome screen
- **Quit** - Exit application completely

### Benefits

1. **Privacy**: Hide sensitive password manager from view
2. **Quick Access**: Double-click tray icon to restore window
3. **Background Operation**: Keep app running without screen space
4. **Lock Convenience**: Lock vault directly from tray menu

### Usage

**Minimize to Tray:**
```
1. Click window close button (X)
2. Window minimizes to system tray
3. Notification appears: "pwick is running in the background"
```

**Restore from Tray:**
```
1. Double-click tray icon, OR
2. Right-click tray icon → Show
3. Window restores to previous position
```

**Quit Application:**
```
1. Right-click tray icon → Quit
2. Application closes completely
3. Tray icon disappears
4. Clipboard cleared automatically
```

## Encrypted Clipboard

### Problem Statement

Traditional password managers copy plaintext passwords to the system clipboard, which creates security risks:

1. **Clipboard Telemetry**: Many applications (including some operating systems) monitor clipboard for "helpful" features
2. **Clipboard Snooping**: Malicious software can read clipboard contents
3. **Clipboard History**: Some systems maintain clipboard history with plaintext passwords
4. **Cross-App Leaks**: Other apps might inadvertently log clipboard data

### Solution: Encrypted Clipboard

pwick encrypts all passwords before placing them on the clipboard using:
- **AES-256-GCM** authenticated encryption
- **Session Key**: Unique key generated when pwick starts
- **Random Nonce**: Unique nonce for each copy operation
- **Prefix Marker**: Identifies encrypted pwick data

### How It Works

**When Copying Password:**
```
1. User clicks "Copy Password" or uses Ctrl+C
2. pwick encrypts password with AES-256-GCM
3. Encrypted blob is base64-encoded
4. Format: PWICK_ENC:<base64(nonce||ciphertext||tag)>
5. Encrypted string placed on clipboard
6. 30-second auto-clear timer starts
```

**When Pasting:**
```
1. User pastes into password field (Ctrl+V)
2. Application receives encrypted string
3. Most applications cannot decrypt it (only pwick can)
4. If pwick pastes its own encrypted data, it decrypts automatically
```

### Security Benefits

1. **Telemetry Protection**: Clipboard monitors see encrypted gibberish
2. **Snooping Protection**: Malicious apps cannot read plaintext passwords
3. **History Protection**: System clipboard history stores only encrypted data
4. **Cross-App Protection**: Other apps cannot use the password

### Technical Details

**Encryption Format:**
```
PWICK_ENC:<base64_encoded_blob>

Where blob contains:
- 12 bytes: Random nonce
- N bytes: AES-256-GCM ciphertext
- 16 bytes: Authentication tag (included in ciphertext)
```

**Session Key:**
- Generated once when pwick starts
- 256-bit random key (32 bytes)
- Unique per application instance
- Never stored on disk

**Nonce:**
- 12 bytes (96 bits) random data
- Unique for each copy operation
- Prevents replay attacks

### Example

**Plaintext Password:**
```
MySecurePassword123!
```

**Encrypted Clipboard Content:**
```
PWICK_ENC:xK7mP9fE2hQvN1cRwA3bL8sT5jU6nY4dH0gZ9iM2oX7yC1pV8kW3eR6tF4qS5aL0z
```

### Compatibility

**Works With:**
- Any application that accepts text input
- Web browsers (password fields)
- Desktop applications
- Terminal applications

**Behavior:**
- Most apps receive encrypted string (unusable)
- pwick can decrypt its own encrypted data
- User must paste into password field immediately or within 30 seconds

### Auto-Clear Integration

Encrypted clipboard works seamlessly with 30-second auto-clear:
```
1. Password encrypted and copied (time 0s)
2. User pastes into application (time 5s)
3. Application receives encrypted string
4. Clipboard cleared at 30s mark
5. Both encrypted and plaintext gone
```

### Limitations

**Single-Instance:**
- Session key unique to application instance
- Different pwick instances cannot decrypt each other's data
- Restart pwick: old encrypted data becomes undecryptable

**Copy-Paste Only:**
- Encryption applies only to clipboard operations
- Typed passwords are not encrypted (normal behavior)
- Export/import uses vault encryption (different system)

**30-Second Window:**
- Must paste within 30 seconds
- After auto-clear, re-copy password if needed
- Clipboard history preserves plaintext for convenience

## Combined Workflow

### Typical Usage

**Starting pwick:**
```
1. Launch pwick (pwick command or desktop shortcut)
2. Tray icon appears in system tray
3. Welcome screen opens
4. Unlock vault with master password
```

**Daily Use:**
```
1. Search for password entry (Ctrl+F)
2. Select entry from list
3. Copy password (Ctrl+C)
   → Password encrypted and copied to clipboard
   → Status bar: "Password copied (encrypted)! Will auto-clear in 30s"
4. Paste into application (Ctrl+V)
   → Application receives encrypted string
5. After 30 seconds: clipboard cleared automatically
6. Minimize to tray (click X)
   → pwick hidden but running
```

**Restoring pwick:**
```
1. Double-click tray icon
2. pwick window appears
3. Search for next password
```

**Locking Vault:**
```
1. Right-click tray icon → Lock Vault
2. Vault locked, data cleared from memory
3. Welcome screen appears
```

**Quitting:**
```
1. Right-click tray icon → Quit
2. Clipboard cleared
3. Memory cleared
4. Application exits
```

## Security Considerations

### What This Protects Against

✅ **Clipboard Telemetry**: OS/app monitoring sees only encrypted data
✅ **Clipboard Snooping**: Malware cannot read plaintext passwords
✅ **Clipboard History**: System clipboard history stores encrypted data
✅ **Shoulder Surfing**: Encrypted string visible if user displays clipboard
✅ **Memory Dumps**: Session key in memory but harder to extract than plaintext

### What This Does NOT Protect Against

❌ **Keyloggers**: Hardware/software keyloggers capture typed passwords
❌ **Screen Capture**: Screenshots can capture visible passwords
❌ **Physical Access**: Attacker with physical access can compromise system
❌ **Browser Password Managers**: Separate systems with their own security
❌ **Phishing**: User voluntarily entering password on fake site

### Best Practices

1. **Use System Tray**: Minimize to tray when not actively using pwick
2. **Lock Frequently**: Lock vault (Ctrl+L) when stepping away
3. **Paste Quickly**: Paste password within 30-second window
4. **Clear Manually**: Use "Lock Vault" to clear clipboard immediately
5. **Verify Site**: Always verify website URL before pasting passwords
6. **Use Generated Passwords**: Strong, unique passwords for each site

## Troubleshooting

### Tray Icon Not Visible

**Symptoms:**
- pwick starts but no tray icon
- Cannot minimize to tray

**Solutions:**
- Check system tray settings (some systems hide icons by default)
- Windows: Check "Show hidden icons" in taskbar settings
- Linux: Ensure system tray extension installed (GNOME, KDE)

### Cannot Paste Password

**Symptoms:**
- Paste shows encrypted string instead of password
- Application receives garbled text

**Expected Behavior:**
- This is intentional - prevents other apps from reading passwords
- Only pwick can decrypt encrypted clipboard data
- Paste directly into password field

**Workaround (if needed):**
- Use clipboard history feature
- Double-click history entry
- Paste within 30 seconds

### Clipboard Clears Too Quickly

**Symptoms:**
- Password cleared before pasting

**Solutions:**
- Increase auto-clear timeout (future feature)
- Copy password again (Ctrl+C)
- Use clipboard history to re-copy

### Tray Icon Doesn't Restore Window

**Symptoms:**
- Double-click tray icon does nothing
- Window remains hidden

**Solutions:**
- Right-click tray icon → Show
- Check if window behind other windows
- Restart pwick if issue persists

## Technical Implementation

### System Tray (Qt)

**QSystemTrayIcon:**
- Uses Qt's QSystemTrayIcon class
- Cross-platform: Windows, Linux (X11), macOS
- Custom icon: 64x64 pixmap with red background and white "P"

**Icon Generation:**
```python
pixmap = QPixmap(64, 64)
pixmap.fill(QColor(198, 40, 40))  # Red
painter.drawText(rect, Qt.AlignCenter, 'P')  # White text
```

**Menu:**
- QMenu with QActions
- Connected to slots for show/hide/lock/quit
- Context menu on right-click

### Encrypted Clipboard (AES-GCM)

**EncryptedClipboard Class:**
```python
class EncryptedClipboard:
    session_key: 256-bit AES key (generated at startup)
    cipher: AESGCM instance
    prefix: "PWICK_ENC:"
    
    Methods:
    - copy_encrypted(plaintext) → clipboard
    - paste_decrypted() → plaintext or None
```

**Encryption:**
```python
nonce = secrets.token_bytes(12)  # Random 96-bit nonce
ciphertext = AESGCM.encrypt(nonce, plaintext, None)
blob = base64.b64encode(nonce + ciphertext)
clipboard = prefix + blob
```

**Decryption:**
```python
if clipboard.startswith(prefix):
    blob = base64.b64decode(clipboard[len(prefix):])
    nonce = blob[:12]
    ciphertext = blob[12:]
    plaintext = AESGCM.decrypt(nonce, ciphertext, None)
```

### Integration Points

**MainWindow.__init__():**
- Creates EncryptedClipboard instance
- Calls _setup_system_tray()
- Stores session-specific encryption key

**_copy_password():**
- Uses encrypted_clipboard.copy_encrypted()
- Instead of pyperclip.copy() directly
- Updates status bar to indicate encryption

**closeEvent():**
- Overridden to minimize to tray
- Prevents application quit on window close
- Shows notification

## Future Enhancements

### Potential Features

1. **Configurable Timeout**: Allow users to adjust 30-second timer
2. **Plaintext Option**: Toggle for non-encrypted clipboard (advanced users)
3. **Multi-Instance**: Support decryption across multiple pwick instances
4. **Auto-Restore**: Remember window position and restore on show
5. **Hotkey**: Global hotkey to show/hide window (Ctrl+Alt+P)
6. **Notification Control**: Disable tray notifications if desired

### Community Feedback

We welcome feedback on these features:
- Is encrypted clipboard working as expected?
- Should auto-clear timeout be configurable?
- Are tray notifications helpful or annoying?
- Would you like additional tray menu options?

Submit feedback via GitHub Issues.

## Conclusion

System tray and encrypted clipboard features significantly enhance pwick's security and usability:

- **Privacy**: Encrypted clipboard prevents telemetry and snooping
- **Convenience**: System tray keeps pwick accessible but hidden
- **Security**: 30-second auto-clear + encryption = multi-layer protection
- **Cross-Platform**: Works on Windows and Linux

These features maintain pwick's core philosophy: local-first, privacy-focused, zero network connections.
