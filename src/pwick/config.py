"""
pwick.config - Configuration management for pwick.

Handles user settings stored in TOML format in OS-appropriate config directory.
Settings include auto-lock timeout, clipboard settings, password generator preferences, etc.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Import tomli for reading TOML (built-in for Python 3.11+)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# Import tomli_w for writing TOML
try:
    import tomli_w
except ImportError:
    tomli_w = None


def get_config_dir() -> Path:
    """
    Get the OS-appropriate configuration directory for pwick.

    Returns:
        Path object pointing to config directory

    Locations:
        Linux/Mac: ~/.config/pwick/
        Windows: %APPDATA%/pwick/
    """
    if sys.platform == 'win32':
        # Windows: use APPDATA
        appdata = os.getenv('APPDATA')
        if appdata:
            return Path(appdata) / 'pwick'
        else:
            # Fallback to home directory
            return Path.home() / 'pwick'
    else:
        # Linux/Mac: use XDG_CONFIG_HOME or default to ~/.config
        xdg_config = os.getenv('XDG_CONFIG_HOME')
        if xdg_config:
            return Path(xdg_config) / 'pwick'
        else:
            return Path.home() / '.config' / 'pwick'


def get_config_path() -> Path:
    """
    Get the full path to the settings.toml configuration file.

    Returns:
        Path object pointing to settings.toml
    """
    return get_config_dir() / 'settings.toml'


def get_default_settings() -> Dict[str, Any]:
    """
    Get default settings for pwick.

    Returns:
        Dictionary containing all default settings
    """
    return {
        # General settings
        'auto_lock_minutes': 5,
        'clipboard_clear_seconds': 30,
        'clipboard_history_size': 30,

        # Password generator settings
        'password_generator_length': 20,
        'password_generator_use_uppercase': True,
        'password_generator_use_lowercase': True,
        'password_generator_use_digits': True,
        'password_generator_use_punctuation': True,

        # Appearance settings
        'theme': 'dark',  # Future: 'light' option

        # Advanced security settings (Argon2id parameters for new vaults)
        'vault_argon2_time_cost': 3,
        'vault_argon2_memory_cost': 65536,  # 64 MB
        'vault_argon2_parallelism': 1,
        'vault_argon2_hash_len': 32,
    }


def load_settings() -> Dict[str, Any]:
    """
    Load settings from configuration file.

    If config file doesn't exist or can't be read, returns default settings.
    If config file exists but has missing keys, fills in defaults for missing keys.

    Returns:
        Dictionary containing user settings
    """
    if tomllib is None:
        # TOML library not available, use defaults
        return get_default_settings()

    config_path = get_config_path()

    if not config_path.exists():
        # Config file doesn't exist, use defaults
        return get_default_settings()

    try:
        with open(config_path, 'rb') as f:
            user_settings = tomllib.load(f)

        # Merge with defaults to ensure all keys exist
        default_settings = get_default_settings()
        for key in default_settings:
            if key not in user_settings:
                user_settings[key] = default_settings[key]

        return user_settings

    except Exception as e:
        # Error reading config, use defaults
        print(f"Warning: Could not load settings from {config_path}: {e}")
        print("Using default settings.")
        return get_default_settings()


def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Save settings to configuration file.

    Creates config directory if it doesn't exist.

    Args:
        settings: Dictionary containing settings to save

    Returns:
        True if save successful, False otherwise
    """
    if tomli_w is None:
        print("Error: tomli_w not available. Cannot save settings.")
        return False

    config_dir = get_config_dir()
    config_path = get_config_path()

    try:
        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        # Write settings to TOML file
        with open(config_path, 'wb') as f:
            tomli_w.dump(settings, f)

        return True

    except Exception as e:
        print(f"Error: Could not save settings to {config_path}: {e}")
        return False


def reset_settings() -> bool:
    """
    Reset settings to defaults by deleting the config file.

    Returns:
        True if reset successful, False otherwise
    """
    config_path = get_config_path()

    try:
        if config_path.exists():
            config_path.unlink()
        return True
    except Exception as e:
        print(f"Error: Could not reset settings: {e}")
        return False


def validate_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate settings and ensure all values are within acceptable ranges.

    Args:
        settings: Dictionary of settings to validate

    Returns:
        Validated settings dictionary with corrections applied
    """
    validated = settings.copy()

    # Validate auto_lock_minutes (0 to disable, or 1-1440 minutes)
    if validated['auto_lock_minutes'] < 0:
        validated['auto_lock_minutes'] = 0
    elif validated['auto_lock_minutes'] > 1440:  # 24 hours max
        validated['auto_lock_minutes'] = 1440

    # Validate clipboard_clear_seconds (10-600 seconds)
    if validated['clipboard_clear_seconds'] < 10:
        validated['clipboard_clear_seconds'] = 10
    elif validated['clipboard_clear_seconds'] > 600:  # 10 minutes max
        validated['clipboard_clear_seconds'] = 600

    # Validate clipboard_history_size (0-100)
    if validated['clipboard_history_size'] < 0:
        validated['clipboard_history_size'] = 0
    elif validated['clipboard_history_size'] > 100:
        validated['clipboard_history_size'] = 100

    # Validate password_generator_length (8-128)
    if validated['password_generator_length'] < 8:
        validated['password_generator_length'] = 8
    elif validated['password_generator_length'] > 128:
        validated['password_generator_length'] = 128

    # Ensure at least one character set is enabled for password generator
    if not any([
        validated['password_generator_use_uppercase'],
        validated['password_generator_use_lowercase'],
        validated['password_generator_use_digits'],
        validated['password_generator_use_punctuation']
    ]):
        # Re-enable all character sets if none are enabled
        validated['password_generator_use_uppercase'] = True
        validated['password_generator_use_lowercase'] = True
        validated['password_generator_use_digits'] = True
        validated['password_generator_use_punctuation'] = True

    # Validate Argon2id parameters
    if validated['vault_argon2_time_cost'] < 1:
        validated['vault_argon2_time_cost'] = 1
    elif validated['vault_argon2_time_cost'] > 10:
        validated['vault_argon2_time_cost'] = 10

    if validated['vault_argon2_memory_cost'] < 8192:  # 8 MB min
        validated['vault_argon2_memory_cost'] = 8192
    elif validated['vault_argon2_memory_cost'] > 1048576:  # 1 GB max
        validated['vault_argon2_memory_cost'] = 1048576

    if validated['vault_argon2_parallelism'] < 1:
        validated['vault_argon2_parallelism'] = 1
    elif validated['vault_argon2_parallelism'] > 16:
        validated['vault_argon2_parallelism'] = 16

    if validated['vault_argon2_hash_len'] < 16:
        validated['vault_argon2_hash_len'] = 16
    elif validated['vault_argon2_hash_len'] > 64:
        validated['vault_argon2_hash_len'] = 64

    return validated
