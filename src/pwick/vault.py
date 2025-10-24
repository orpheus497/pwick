"""
pwick - A simple, secure, and 100% local password manager.
Core vault functionality with Argon2id key derivation and AES-256-GCM encryption.
"""

import json
import os
import base64
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type


class VaultError(Exception):
    """Base exception for vault operations."""
    pass


class VaultAuthenticationError(VaultError):
    """Raised when master password is incorrect."""
    pass


def _derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Derive a 32-byte encryption key from the master password using Argon2id.
    
    Parameters:
        time_cost=3, memory_cost=65536 KB, parallelism=1
    """
    return hash_secret_raw(
        secret=master_password.encode('utf-8'),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )


def _encrypt_data(data: bytes, key: bytes) -> Dict[str, str]:
    """
    Encrypt data using AES-256-GCM.
    Returns dict with base64-encoded nonce and ciphertext.
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    return {
        'nonce': base64.b64encode(nonce).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
    }


def _decrypt_data(encrypted_data: Dict[str, str], key: bytes) -> bytes:
    """
    Decrypt data using AES-256-GCM.
    """
    aesgcm = AESGCM(key)
    nonce = base64.b64decode(encrypted_data['nonce'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext
    except Exception as e:
        raise VaultAuthenticationError("Failed to decrypt vault. Incorrect master password or corrupted data.")


def create_vault(path: str, master_password: str) -> Dict[str, Any]:
    """
    Create a new encrypted vault file.
    
    Returns the vault object (for immediate use without reloading).
    """
    if os.path.exists(path):
        raise VaultError(f"Vault already exists at {path}")
    
    # Create vault structure
    vault = {
        'metadata': {
            'version': '1.0',
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        'entries': []
    }
    
    save_vault(path, vault, master_password)
    return vault


def save_vault(path: str, vault_obj: Dict[str, Any], master_password: str) -> None:
    """
    Save vault to encrypted file.
    """
    # Generate salt
    salt = os.urandom(16)
    
    # Derive key
    key = _derive_key(master_password, salt)
    
    # Serialize vault to JSON
    vault_json = json.dumps(vault_obj, indent=2)
    
    # Encrypt
    encrypted = _encrypt_data(vault_json.encode('utf-8'), key)
    
    # Create file structure
    vault_file = {
        'salt': base64.b64encode(salt).decode('utf-8'),
        'data': encrypted
    }
    
    # Write to file
    with open(path, 'w') as f:
        json.dump(vault_file, f, indent=2)


def load_vault(path: str, master_password: str) -> Dict[str, Any]:
    """
    Load and decrypt vault from file.
    """
    if not os.path.exists(path):
        raise VaultError(f"Vault not found at {path}")
    
    # Read vault file
    with open(path, 'r') as f:
        vault_file = json.load(f)
    
    # Extract salt
    salt = base64.b64decode(vault_file['salt'])
    
    # Derive key
    key = _derive_key(master_password, salt)
    
    # Decrypt
    vault_json = _decrypt_data(vault_file['data'], key)
    
    # Parse JSON
    vault = json.loads(vault_json.decode('utf-8'))
    
    return vault


def add_entry(vault: Dict[str, Any], title: str, username: str = "", 
              password: str = "", notes: str = "", entry_type: str = "password") -> str:
    """
    Add a new entry to the vault.
    Returns the entry ID.
    """
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    entry = {
        'id': entry_id,
        'type': entry_type,
        'title': title,
        'username': username,
        'password': password,
        'notes': notes,
        'created_at': now,
        'updated_at': now
    }
    
    vault['entries'].append(entry)
    return entry_id


def update_entry(vault: Dict[str, Any], entry_id: str, title: Optional[str] = None,
                username: Optional[str] = None, password: Optional[str] = None,
                notes: Optional[str] = None, entry_type: Optional[str] = None) -> bool:
    """
    Update an existing entry.
    Returns True if entry was found and updated, False otherwise.
    """
    for entry in vault['entries']:
        if entry['id'] == entry_id:
            if title is not None:
                entry['title'] = title
            if username is not None:
                entry['username'] = username
            if password is not None:
                entry['password'] = password
            if notes is not None:
                entry['notes'] = notes
            if entry_type is not None:
                entry['type'] = entry_type
            entry['updated_at'] = datetime.now(timezone.utc).isoformat()
            return True
    return False

def add_note(vault: Dict[str, Any], title: str, content: str) -> str:
    """
    Add a new note entry to the vault.
    Returns the entry ID.
    """
    return add_entry(vault, title, notes=content, entry_type="note")

def update_note(vault: Dict[str, Any], entry_id: str, title: Optional[str] = None,
                content: Optional[str] = None) -> bool:
    """
    Update an existing note entry.
    Returns True if entry was found and updated, False otherwise.
    """
    return update_entry(vault, entry_id, title=title, notes=content, entry_type="note")


def delete_entry(vault: Dict[str, Any], entry_id: str) -> bool:
    """
    Delete an entry from the vault.
    Returns True if entry was found and deleted, False otherwise.
    """
    for i, entry in enumerate(vault['entries']):
        if entry['id'] == entry_id:
            vault['entries'].pop(i)
            return True
    return False


def export_encrypted(path: str, target_path: str, master_password: str) -> None:
    """
    Export vault to a new encrypted file (for backup/transfer).
    This is essentially a copy operation.
    """
    vault = load_vault(path, master_password)
    save_vault(target_path, vault, master_password)


def import_encrypted(source_path: str, target_path: str, master_password: str) -> Dict[str, Any]:
    """
    Import an encrypted vault file to a new location.
    Returns the loaded vault object.
    """
    vault = load_vault(source_path, master_password)
    save_vault(target_path, vault, master_password)
    return vault
