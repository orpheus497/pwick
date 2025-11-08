"""
System theme detection for pwick.

Detects the current system theme (dark/light) on Windows, Linux, and macOS
to automatically match the application theme to the user's system preferences.
"""

from __future__ import annotations

import sys
import os
import subprocess
from typing import Literal

ThemeMode = Literal["dark", "light", "unknown"]


def detect_system_theme() -> ThemeMode:
    """
    Detect the current system theme.

    Returns:
        "dark", "light", or "unknown" if detection fails

    Platform-specific detection:
        - Windows: Reads AppsUseLightTheme registry key
        - macOS: Reads AppleInterfaceStyle from defaults
        - Linux: Reads GTK theme or gsettings
    """
    if sys.platform == "win32":
        return _detect_windows_theme()
    elif sys.platform == "darwin":
        return _detect_macos_theme()
    else:  # Linux and other Unix-like systems
        return _detect_linux_theme()


def _detect_windows_theme() -> ThemeMode:
    """
    Detect Windows system theme from registry.

    Reads HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize
    AppsUseLightTheme value (0 = dark, 1 = light)
    """
    try:
        import winreg

        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path)

        value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
        winreg.CloseKey(registry_key)

        # 0 = dark mode, 1 = light mode
        return "light" if value == 1 else "dark"

    except (ImportError, FileNotFoundError, OSError):
        # Registry key doesn't exist or winreg not available
        return "unknown"


def _detect_macos_theme() -> ThemeMode:
    """
    Detect macOS system theme using defaults command.

    Reads AppleInterfaceStyle from user defaults.
    If not set, system is in light mode.
    """
    try:
        # Run: defaults read -g AppleInterfaceStyle
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
            timeout=2
        )

        # If the key exists and contains "Dark", system is in dark mode
        if result.returncode == 0 and "Dark" in result.stdout:
            return "dark"
        else:
            # Key doesn't exist or doesn't contain "Dark" = light mode
            return "light"

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def _detect_linux_theme() -> ThemeMode:
    """
    Detect Linux system theme.

    Tries multiple methods in order:
    1. gsettings (GNOME/GTK)
    2. GTK_THEME environment variable
    3. ~/.config/gtk-3.0/settings.ini
    4. KDE plasma theme (for KDE Plasma)
    """
    # Method 1: Try gsettings (GNOME/GTK-based desktops)
    theme = _detect_linux_gsettings()
    if theme != "unknown":
        return theme

    # Method 2: Check GTK_THEME environment variable
    gtk_theme = os.getenv("GTK_THEME", "").lower()
    if "dark" in gtk_theme:
        return "dark"
    elif gtk_theme:
        return "light"

    # Method 3: Check GTK settings file
    theme = _detect_linux_gtk_settings()
    if theme != "unknown":
        return theme

    # Method 4: Try KDE Plasma
    theme = _detect_linux_kde_theme()
    if theme != "unknown":
        return theme

    return "unknown"


def _detect_linux_gsettings() -> ThemeMode:
    """Detect theme using gsettings (GNOME/GTK)."""
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            theme_name = result.stdout.strip().strip("'\"").lower()
            if "dark" in theme_name:
                return "dark"
            elif theme_name:
                return "light"

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    # Also check color-scheme setting (newer GNOME versions)
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            scheme = result.stdout.strip().strip("'\"").lower()
            if "dark" in scheme or "prefer-dark" in scheme:
                return "dark"
            elif "light" in scheme or "prefer-light" in scheme:
                return "light"

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return "unknown"


def _detect_linux_gtk_settings() -> ThemeMode:
    """Detect theme from GTK settings file."""
    try:
        from pathlib import Path

        # Check ~/.config/gtk-3.0/settings.ini
        gtk_settings = Path.home() / ".config" / "gtk-3.0" / "settings.ini"

        if gtk_settings.exists():
            content = gtk_settings.read_text()

            # Look for gtk-theme-name or gtk-application-prefer-dark-theme
            for line in content.split('\n'):
                line = line.strip().lower()

                if line.startswith('gtk-application-prefer-dark-theme'):
                    if 'true' in line or '1' in line:
                        return "dark"
                    else:
                        return "light"

                if line.startswith('gtk-theme-name'):
                    if 'dark' in line:
                        return "dark"
                    elif '=' in line:  # Theme is set
                        return "light"

    except Exception:
        pass

    return "unknown"


def _detect_linux_kde_theme() -> ThemeMode:
    """Detect theme for KDE Plasma desktop."""
    try:
        # Check KDE color scheme
        result = subprocess.run(
            ["kreadconfig5", "--group", "General", "--key", "ColorScheme"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            scheme = result.stdout.strip().lower()
            if "dark" in scheme or "breeze dark" in scheme:
                return "dark"
            elif scheme:
                return "light"

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return "unknown"


def is_dark_theme_preferred() -> bool:
    """
    Check if dark theme is preferred by the system.

    Returns:
        True if dark theme is detected, False if light or unknown
    """
    return detect_system_theme() == "dark"


def get_auto_theme() -> Literal["dark", "light"]:
    """
    Get the appropriate theme based on system detection.

    Returns:
        "dark" or "light" (defaults to "dark" if detection fails)
    """
    theme = detect_system_theme()

    if theme == "unknown":
        # Default to dark theme if detection fails
        return "dark"

    return theme
