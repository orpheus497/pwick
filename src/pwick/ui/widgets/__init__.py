"""
pwick.ui.widgets - Widget package for pwick UI dialogs.

This package contains all custom dialog widgets used by the main window
including welcome, password entry, master password, settings, and other dialogs.
"""

from .welcome_dialog import WelcomeDialog
from .master_password_dialog import MasterPasswordDialog
from .entry_dialog import EntryDialog
from .settings_dialog import SettingsDialog
from .security_audit_dialog import SecurityAuditDialog
from .password_history_dialog import PasswordHistoryDialog
from .password_strength_widget import PasswordStrengthWidget

__all__ = [
    "WelcomeDialog",
    "MasterPasswordDialog",
    "EntryDialog",
    "SettingsDialog",
    "SecurityAuditDialog",
    "PasswordHistoryDialog",
    "PasswordStrengthWidget",
]
