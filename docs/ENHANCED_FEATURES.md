# Enhanced Features Documentation

## Clipboard Auto-Clear (30 seconds)

When you copy a password using the "Copy Password" button or `Ctrl+C` keyboard shortcut, the password is automatically cleared from your clipboard after 30 seconds for enhanced security.

**How it works:**
1. Click "Copy Password" or press `Ctrl+C` when an entry is selected
2. The status bar shows: "Password copied to clipboard! (Will auto-clear in 30s)"
3. After 30 seconds, the clipboard is automatically cleared
4. The status bar briefly shows: "Clipboard cleared for security"

**Benefits:**
- Prevents accidental password exposure if you forget to clear clipboard
- Reduces risk of password leakage through clipboard managers
- Automatic security without user intervention

## Keyboard Shortcuts

pwick now includes convenient keyboard shortcuts for quick access to common actions:

### Main Window Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+C` / `Cmd+C` | Copy Password | Copy the selected entry's password to clipboard (auto-clears after 30s) |
| `Ctrl+N` / `Cmd+N` | New Entry | Open dialog to add a new password entry |
| `Ctrl+E` / `Cmd+E` | Edit Entry | Edit the currently selected entry |
| `Delete` / `Del` | Delete Entry | Delete the currently selected entry (with confirmation) |
| `Ctrl+L` / `Cmd+L` | Lock Vault | Lock the vault and return to welcome screen |
| `Ctrl+F` / `Cmd+F` | Focus List | Focus on the entry list for quick keyboard navigation |

### Dialog Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Confirm/Save |
| `Esc` | Cancel |
| `Tab` | Navigate between fields |

**Benefits:**
- Faster workflow for power users
- Reduce reliance on mouse for common operations
- Standard shortcuts that match other applications
- Cross-platform compatibility (works on Windows, Linux, Mac)

## Implementation Details

### Clipboard Timer
- Uses Qt's `QTimer` with single-shot mode
- 30-second countdown starts when password is copied
- Timer is reset each time a new password is copied
- Clearing is done by setting clipboard to empty string

### Keyboard Shortcuts
- Implemented using Qt's `QShortcut` class
- Uses standard `QKeySequence` constants for cross-platform compatibility
- Shortcuts work globally within the application window
- Does not interfere with system-wide shortcuts

## Security Considerations

### Clipboard Auto-Clear
- **Pro**: Reduces risk of password exposure through clipboard
- **Pro**: Works automatically without user action
- **Con**: May interfere with users who need passwords in clipboard longer
- **Mitigation**: 30 seconds is long enough for most paste operations

### Keyboard Shortcuts
- **Pro**: Reduces time application window is open (faster operations)
- **Pro**: Less visible mouse movements (reduces shoulder surfing risk)
- **Con**: Keyboard shortcuts could be accidentally triggered
- **Mitigation**: Destructive operations (delete) still require confirmation

## Usage Examples

### Quick Copy Workflow
1. Press `Ctrl+F` to focus the entry list
2. Type first few letters of the entry you want (Qt's list widget supports type-ahead)
3. Press `Ctrl+C` to copy the password
4. Switch to your browser/app and paste within 30 seconds
5. Clipboard automatically clears after 30 seconds

### Quick Add Entry
1. Press `Ctrl+N` to open new entry dialog
2. Fill in the fields
3. Press `Enter` to save
4. Entry is immediately available in the list

### Power User Workflow
1. `Ctrl+F` - Focus list
2. Type to find entry
3. `Ctrl+E` - Edit entry
4. Make changes
5. `Enter` - Save
6. `Ctrl+L` - Lock when done

## Testing

To test these features:

1. **Clipboard Auto-Clear**:
   - Select an entry
   - Copy password (button or Ctrl+C)
   - Observe status bar message: "Password copied to clipboard! (Will auto-clear in 30s)"
   - Wait 30 seconds
   - Observe status bar message: "Clipboard cleared for security"
   - Try to paste - clipboard should be empty

2. **Keyboard Shortcuts**:
   - Try each shortcut listed above
   - Verify the corresponding action is triggered
   - Test on different platforms (Windows, Linux, Mac)

## Future Enhancements

Potential future improvements while maintaining local-first philosophy:

1. **Configurable clipboard timeout**: Allow users to adjust the 30-second timeout
2. **Clipboard history prevention**: Add option to prevent clipboard managers from recording passwords
3. **More keyboard shortcuts**: Add shortcuts for search, export, settings
4. **Customizable shortcuts**: Allow users to customize keyboard shortcuts
5. **Keyboard navigation improvements**: Better keyboard-only navigation throughout the app
