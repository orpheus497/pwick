"""
Tests for system theme detection module.

Tests cover:
- Windows theme detection (registry)
- macOS theme detection (defaults command)
- Linux theme detection (gsettings, GTK, KDE)
- Auto theme fallback behavior
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pwick.system_theme import (
    ThemeMode,
    detect_system_theme,
    get_auto_theme,
    _detect_windows_theme,
    _detect_macos_theme,
    _detect_linux_theme,
)


class TestThemeMode:
    """Test ThemeMode literal type."""

    def test_theme_mode_values(self):
        """Test that ThemeMode has expected values."""
        # ThemeMode is a Literal type, so we just verify it's defined
        # and can be used in type annotations
        theme: ThemeMode = "dark"
        assert theme in ["dark", "light", "unknown"]


class TestWindowsThemeDetection:
    """Test Windows theme detection."""

    @patch("pwick.system_theme.sys.platform", "win32")
    @patch("pwick.system_theme.winreg.OpenKey")
    @patch("pwick.system_theme.winreg.QueryValueEx")
    def test_windows_dark_theme(self, mock_query, mock_open):
        """Test Windows dark theme detection."""
        mock_query.return_value = (0, None)  # 0 = Dark theme
        result = _detect_windows_theme()
        assert result == "dark"

    @patch("pwick.system_theme.sys.platform", "win32")
    @patch("pwick.system_theme.winreg.OpenKey")
    @patch("pwick.system_theme.winreg.QueryValueEx")
    def test_windows_light_theme(self, mock_query, mock_open):
        """Test Windows light theme detection."""
        mock_query.return_value = (1, None)  # 1 = Light theme
        result = _detect_windows_theme()
        assert result == "light"

    @patch("pwick.system_theme.sys.platform", "win32")
    @patch("pwick.system_theme.winreg.OpenKey")
    def test_windows_theme_error(self, mock_open):
        """Test Windows theme detection with registry error."""
        mock_open.side_effect = Exception("Registry error")
        result = _detect_windows_theme()
        assert result == "unknown"


class TestMacOSThemeDetection:
    """Test macOS theme detection."""

    @patch("pwick.system_theme.sys.platform", "darwin")
    @patch("pwick.system_theme.subprocess.run")
    def test_macos_dark_theme(self, mock_run):
        """Test macOS dark theme detection."""
        mock_run.return_value = Mock(returncode=0, stdout="Dark\n")
        result = _detect_macos_theme()
        assert result == "dark"

    @patch("pwick.system_theme.sys.platform", "darwin")
    @patch("pwick.system_theme.subprocess.run")
    def test_macos_light_theme(self, mock_run):
        """Test macOS light theme detection (no Dark mode)."""
        mock_run.return_value = Mock(
            returncode=1, stdout=""  # Command fails when not in dark mode
        )
        result = _detect_macos_theme()
        assert result == "light"

    @patch("pwick.system_theme.sys.platform", "darwin")
    @patch("pwick.system_theme.subprocess.run")
    def test_macos_theme_error(self, mock_run):
        """Test macOS theme detection with subprocess error."""
        mock_run.side_effect = Exception("Subprocess error")
        result = _detect_macos_theme()
        assert result == "unknown"


class TestLinuxThemeDetection:
    """Test Linux theme detection."""

    @patch("pwick.system_theme.subprocess.run")
    def test_linux_dark_theme_gsettings(self, mock_run):
        """Test Linux dark theme detection via gsettings."""
        mock_run.return_value = Mock(returncode=0, stdout="prefer-dark\n")
        result = _detect_linux_theme()
        assert result == "dark"

    @patch("pwick.system_theme.subprocess.run")
    def test_linux_light_theme_gsettings(self, mock_run):
        """Test Linux light theme detection via gsettings."""
        mock_run.return_value = Mock(returncode=0, stdout="prefer-light\n")
        result = _detect_linux_theme()
        assert result == "light"

    @patch("pwick.system_theme.subprocess.run")
    def test_linux_default_theme_gsettings(self, mock_run):
        """Test Linux default theme via gsettings."""
        mock_run.return_value = Mock(returncode=0, stdout="default\n")
        result = _detect_linux_theme()
        assert result == "light"  # default maps to light

    @patch("pwick.system_theme.subprocess.run")
    @patch("pwick.system_theme.Path.exists")
    @patch("pwick.system_theme.Path.read_text")
    def test_linux_dark_theme_gtk(self, mock_read, mock_exists, mock_run):
        """Test Linux dark theme detection via GTK settings."""
        # gsettings fails
        mock_run.side_effect = Exception("gsettings not found")

        # GTK config exists
        mock_exists.return_value = True
        mock_read.return_value = "[Settings]\ngtk-application-prefer-dark-theme=1\n"

        result = _detect_linux_theme()
        assert result == "dark"

    @patch("pwick.system_theme.subprocess.run")
    @patch("pwick.system_theme.Path.exists")
    @patch("pwick.system_theme.Path.read_text")
    def test_linux_light_theme_gtk(self, mock_read, mock_exists, mock_run):
        """Test Linux light theme detection via GTK settings."""
        # gsettings fails
        mock_run.side_effect = Exception("gsettings not found")

        # GTK config exists
        mock_exists.return_value = True
        mock_read.return_value = "[Settings]\ngtk-application-prefer-dark-theme=0\n"

        result = _detect_linux_theme()
        assert result == "light"

    @patch("pwick.system_theme.subprocess.run")
    @patch("pwick.system_theme.Path.exists")
    def test_linux_theme_unknown(self, mock_exists, mock_run):
        """Test Linux theme detection when all methods fail."""
        # gsettings fails
        mock_run.side_effect = Exception("gsettings not found")

        # No GTK config
        mock_exists.return_value = False

        result = _detect_linux_theme()
        assert result == "unknown"


class TestSystemThemeDetection:
    """Test cross-platform theme detection."""

    @patch("pwick.system_theme.sys.platform", "win32")
    @patch("pwick.system_theme._detect_windows_theme")
    def test_detect_system_theme_windows(self, mock_windows):
        """Test that Windows detection is called on Windows."""
        mock_windows.return_value = "dark"
        result = detect_system_theme()
        assert result == "dark"
        mock_windows.assert_called_once()

    @patch("pwick.system_theme.sys.platform", "darwin")
    @patch("pwick.system_theme._detect_macos_theme")
    def test_detect_system_theme_macos(self, mock_macos):
        """Test that macOS detection is called on macOS."""
        mock_macos.return_value = "light"
        result = detect_system_theme()
        assert result == "light"
        mock_macos.assert_called_once()

    @patch("pwick.system_theme.sys.platform", "linux")
    @patch("pwick.system_theme._detect_linux_theme")
    def test_detect_system_theme_linux(self, mock_linux):
        """Test that Linux detection is called on Linux."""
        mock_linux.return_value = "dark"
        result = detect_system_theme()
        assert result == "dark"
        mock_linux.assert_called_once()


class TestAutoThemeGetter:
    """Test get_auto_theme function."""

    @patch("pwick.system_theme.detect_system_theme")
    def test_get_auto_theme_dark(self, mock_detect):
        """Test get_auto_theme returns dark when detected."""
        mock_detect.return_value = "dark"
        result = get_auto_theme()
        assert result == "dark"

    @patch("pwick.system_theme.detect_system_theme")
    def test_get_auto_theme_light(self, mock_detect):
        """Test get_auto_theme returns light when detected."""
        mock_detect.return_value = "light"
        result = get_auto_theme()
        assert result == "light"

    @patch("pwick.system_theme.detect_system_theme")
    def test_get_auto_theme_unknown_defaults_to_dark(self, mock_detect):
        """Test get_auto_theme defaults to dark when unknown."""
        mock_detect.return_value = "unknown"
        result = get_auto_theme()
        assert result == "dark"


class TestThemeDetectionIntegration:
    """Integration tests for theme detection."""

    def test_detect_theme_returns_valid_value(self):
        """Test that detect_system_theme always returns valid ThemeMode."""
        result = detect_system_theme()
        assert result in ["dark", "light", "unknown"]

    def test_get_auto_theme_returns_valid_value(self):
        """Test that get_auto_theme always returns dark or light."""
        result = get_auto_theme()
        assert result in ["dark", "light"]
        assert result != "unknown"  # Should never return unknown


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
