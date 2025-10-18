# Clipboard History Feature

## Overview

The Clipboard History feature provides a convenient way to track and reuse recently copied passwords within pwick. This feature maintains a history of the last 30 copied items, automatically refreshing each day for security.

## Features

### 1. Automatic History Tracking
- Every time you copy a password using "Copy Password" button or `Ctrl+C`, it's added to the clipboard history
- Stores up to 30 most recent copies
- Each entry includes:
  - Entry title (which password was copied)
  - Truncated password text (first 50 characters)
  - Timestamp (HH:MM:SS format)
  - Full password text (hidden, but accessible via double-click)

### 2. Daily Refresh
- History automatically clears at the start of each new day
- Ensures that old passwords don't accumulate indefinitely
- Provides a clean slate each day for better security

### 3. Quick Reuse
- Double-click any item in the clipboard history to copy it again
- Automatically restarts the 30-second auto-clear timer
- Shows notification: "Copied from history! (Will auto-clear in 30s)"

## User Interface

### Location
The clipboard history panel is located in the main window's right panel, below the entry details section.

### Display Format
Each history entry shows:
```
[HH:MM:SS] EntryTitle: password_preview...
```

Example:
```
[14:23:45] GitHub: mypassword123...
[14:20:12] Email Account: securepass456...
[14:15:30] Banking App: bank123secure...
```

### Interaction
- **View**: Scroll through the list to see recent copies
- **Copy Again**: Double-click any item to copy its full password
- **Auto-clear**: All copied items are still subject to the 30-second auto-clear

## Implementation Details

### Data Structure
```python
clipboard_history: List[Dict[str, str]] = [
    {
        'title': 'Entry Title',
        'text': 'truncated_preview...',
        'timestamp': 'HH:MM:SS',
        'full_text': 'complete_password_text'
    },
    ...
]
```

### Storage
- History is stored in memory only (not persisted to disk)
- Cleared when:
  - Application is closed
  - Vault is locked
  - A new day begins
  - More than 30 items are accumulated (oldest removed)

### Date Tracking
```python
clipboard_history_date: date  # Tracks current date
max_clipboard_history: int = 30  # Maximum entries
```

## Security Considerations

### Pros
- ✅ Convenient access to recently copied passwords
- ✅ No need to search for and re-copy passwords
- ✅ Daily refresh prevents accumulation
- ✅ Limited to 30 entries maximum

### Cons
- ⚠️ Password previews visible in UI (first 50 chars)
- ⚠️ History remains in memory until cleared
- ⚠️ Multiple passwords visible at once

### Mitigations
- History is cleared daily
- History is cleared when vault is locked
- History is not persisted to disk
- Full passwords only shown when actively copied
- 30-second auto-clear still applies to all copies

## Usage Examples

### Example 1: Quick Password Reuse
1. Copy password for "Email Account"
2. Use it in your email client
3. Need same password for mobile app
4. Double-click "Email Account" in clipboard history
5. Password re-copied without searching

### Example 2: Multiple Account Setup
1. Setting up multiple accounts with same password
2. Copy password once
3. Use it for first account
4. Clipboard auto-clears after 30s
5. Double-click history entry to copy again
6. Use for second account
7. Repeat as needed

### Example 3: Daily Security
1. Day 1: Copy several passwords throughout the day
2. History accumulates up to 30 entries
3. Day 2: Application starts
4. History automatically cleared
5. Fresh slate for new day

## Configuration

Currently, the following settings are hardcoded:
- **Max History**: 30 entries
- **Refresh Period**: Daily (at midnight)
- **Display Truncation**: 50 characters

Future enhancements could make these configurable.

## Future Enhancements

Potential improvements while maintaining security:

1. **Configurable History Size**: Allow users to adjust the 30-entry limit
2. **Search History**: Add search/filter for clipboard history
3. **Clear History Button**: Manual clear without waiting for daily refresh
4. **Export History**: Export history for audit purposes (encrypted)
5. **Password Masking**: Option to fully mask passwords in history list
6. **Time-based Clear**: Clear history after X hours of inactivity

## Comparison with Other Features

| Feature | Purpose | Retention | Security |
|---------|---------|-----------|----------|
| Clipboard History | Quick reuse | Up to 30 entries, daily clear | Medium (visible in UI) |
| Clipboard Auto-clear | Security | 30 seconds | High (auto-clears) |
| Vault Storage | Persistence | Permanent (until deleted) | Highest (encrypted at rest) |

## Best Practices

1. **Lock Vault When Idle**: History is cleared when vault is locked
2. **Be Aware of Shoulder Surfing**: Password previews are visible in UI
3. **Use in Private**: Don't use clipboard history in public/shared spaces
4. **Regular Locking**: Lock vault regularly to clear history
5. **Daily Workflow**: Rely on daily refresh for automatic cleanup

## Troubleshooting

### History Not Updating
- Ensure vault is unlocked
- Check that you're using "Copy Password" or Ctrl+C
- Verify clipboard history panel is visible

### History Not Clearing Daily
- Check system date/time settings
- Restart application if date changed while running

### Double-click Not Working
- Ensure item is selected
- Try single-click to select, then double-click
- Check if clipboard functionality is working

## Technical Notes

### Thread Safety
- All clipboard operations run on the main UI thread
- No threading issues with history updates

### Memory Usage
- Each entry: ~200 bytes (estimate)
- 30 entries: ~6 KB
- Negligible memory impact

### Performance
- History refresh: O(n) where n = number of entries
- Maximum n = 30, so very fast
- No performance concerns

## Conclusion

The Clipboard History feature provides a convenient way to manage recently copied passwords while maintaining reasonable security through daily refresh and the 30-second auto-clear mechanism. It's designed to be a productivity enhancer without compromising pwick's core security principles.
