# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for pwick password manager.

This file configures PyInstaller to create standalone executables for pwick.

Usage:
    pyinstaller pwick.spec

The resulting executable will be in the 'dist' folder.
"""

import sys
from pathlib import Path

block_cipher = None

# Determine if we're building for console or windowed mode
# On Windows, use windowed mode to hide console
# On Linux/macOS, use console mode for better error reporting
console_mode = sys.platform != 'win32'

# Read version from VERSION file
version_file = Path('VERSION')
if version_file.exists():
    version = version_file.read_text().strip()
else:
    version = '2.4.0'

a = Analysis(
    ['src/pwick/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('VERSION', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.primitives.ciphers.aead',
        'argon2',
        'argon2._ffi',
        'argon2.low_level',
        'pyperclip',
        'zxcvbn',
        'tomli',
        'tomli_w',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pwick',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console_mode,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Metadata for Windows
    version=version,
    icon=None,  # Add icon file path if available
)
