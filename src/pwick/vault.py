"""
pwick - A simple, secure, and 100% local password manager.
Core vault functionality with Argon2id key derivation and AES-256-GCM encryption.
"""

import json
import os
import base64
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TypedDict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type as Argon2Type

# OWASP recommendations for Argon2id as of 2025
# https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536  # 64 MB
ARGON2_PARALLELISM = 1
ARGON2_HASH_LEN = 32
ARGON2_SALT_LEN = 16


class VaultError(Exception):
    """Base exception for vault operations."""
    pass


class VaultAuthenticationError(VaultError):
    """Raised when master password is incorrect."""
    pass


class Argon2Params(TypedDict):
    time_cost: int
    memory_cost: int
    parallelism: int
    hash_len: int


class Entry(TypedDict):
    id: str
    type: str
    title: str
    username: str
    password: str
    notes: str
    created_at: str
    updated_at: str
    tags: List[str]
    pinned: bool
    password_history: List[Dict[str, str]]


class VaultMetadata(TypedDict):
    version: str
    created_at: str
    argon2_params: Argon2Params


class Vault(TypedDict):
    metadata: VaultMetadata
    entries: List[Entry]


def _derive_key(master_password: str, salt: bytes, params: Argon2Params) -> bytes:
    """
    Derive a 32-byte encryption key from the master password using Argon2id.
    """
    return hash_secret_raw(
        secret=master_password.encode('utf-8'),
        salt=salt,
        time_cost=params['time_cost'],
        memory_cost=params['memory_cost'],
        parallelism=params['parallelism'],
        hash_len=params['hash_len'],
        type=Argon2Type.ID
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
        raise VaultAuthenticationError("Failed to decrypt vault. Incorrect master password or corrupted data.") from e


def create_vault(path: str, master_password: str) -> Vault:
    """
    Create a new encrypted vault file.
    
    Returns the vault object (for immediate use without reloading).
    """
    if os.path.exists(path):
        raise VaultError(f"Vault already exists at {path}")
    
    argon2_params: Argon2Params = {
        'time_cost': ARGON2_TIME_COST,
        'memory_cost': ARGON2_MEMORY_COST,
        'parallelism': ARGON2_PARALLELISM,
        'hash_len': ARGON2_HASH_LEN
    }
    
    vault: Vault = {
        'metadata': {
            'version': '2.0',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'argon2_params': argon2_params
        },
        'entries': []
    }
    
    save_vault(path, vault, master_password)
    return vault


def save_vault(path: str, vault_obj: Vault, master_password: str) -> None:
    """
    Save vault to encrypted file.
    """
    salt = os.urandom(ARGON2_SALT_LEN)
    params = vault_obj['metadata']['argon2_params']
    key = _derive_key(master_password, salt, params)
    
    vault_json = json.dumps(vault_obj, indent=2)
    encrypted = _encrypt_data(vault_json.encode('utf-8'), key)
    
    vault_file = {
        'salt': base64.b64encode(salt).decode('utf-8'),
        'argon2_params': params,
        'data': encrypted
    }
    
    with open(path, 'w') as f:
        json.dump(vault_file, f, indent=2)


def load_vault(path: str, master_password: str) -> Vault:
    """
    Load and decrypt vault from file.
    """
    if not os.path.exists(path):
        raise VaultError(f"Vault not found at {path}")
    
    with open(path, 'r') as f:
        vault_file = json.load(f)
    
    salt = base64.b64decode(vault_file['salt'])
    
    # For backward compatibility with version 1.0 vaults that don't have params stored
    params = vault_file.get('argon2_params', {
        'time_cost': 3,
        'memory_cost': 65536,
        'parallelism': 1,
        'hash_len': 32
    })

    key = _derive_key(master_password, salt, params)
    
    vault_json = _decrypt_data(vault_file['data'], key)
    
    vault: Vault = json.loads(vault_json.decode('utf-8'))
    
    return vault


def add_entry(vault: Vault, title: str, username: str = "",
              password: str = "", notes: str = "", entry_type: str = "password",
              tags: Optional[List[str]] = None, pinned: bool = False) -> str:
    """
    Add a new entry to the vault.
    Returns the entry ID.
    """
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    entry: Entry = {
        'id': entry_id,
        'type': entry_type,
        'title': title,
        'username': username,
        'password': password,
        'notes': notes,
        'created_at': now,
        'updated_at': now,
        'tags': tags if tags is not None else [],
        'pinned': pinned,
        'password_history': []
    }

    vault['entries'].append(entry)
    return entry_id


def update_entry(vault: Vault, entry_id: str, **kwargs: Any) -> bool:
    """
    Update an existing entry.
    If password is being updated, saves old password to history.
    Returns True if entry was found and updated, False otherwise.
    """
    for entry in vault['entries']:
        if entry['id'] == entry_id:
            # If password is being changed, save old password to history
            if 'password' in kwargs and kwargs['password'] != entry.get('password', ''):
                old_password = entry.get('password', '')
                if old_password:  # Only save non-empty passwords
                    add_password_to_history(entry, old_password)

            for key, value in kwargs.items():
                if key in entry:
                    entry[key] = value

            entry['updated_at'] = datetime.now(timezone.utc).isoformat()
            return True
    return False


def add_password_to_history(entry: Entry, old_password: str, max_history: int = 5) -> None:
    """
    Add a password to the entry's history.

    Args:
        entry: The entry to update
        old_password: The password to add to history
        max_history: Maximum number of passwords to keep in history (default: 5)
    """
    if 'password_history' not in entry:
        entry['password_history'] = []

    history_item = {
        'password': old_password,
        'changed_at': datetime.now(timezone.utc).isoformat()
    }

    # Add to beginning of list
    entry['password_history'].insert(0, history_item)

    # Keep only the last max_history items
    if len(entry['password_history']) > max_history:
        entry['password_history'] = entry['password_history'][:max_history]

def add_note(vault: Vault, title: str, content: str) -> str:
    """
    Add a new note entry to the vault.
    Returns the entry ID.
    """
    return add_entry(vault, title, notes=content, entry_type="note")

def update_note(vault: Vault, entry_id: str, title: Optional[str] = None,
                content: Optional[str] = None) -> bool:
    """
    Update an existing note entry.
    Returns True if entry was found and updated, False otherwise.
    """
    updates = {}
    if title is not None:
        updates['title'] = title
    if content is not None:
        updates['notes'] = content
    
    if not updates:
        return False
        
    return update_entry(vault, entry_id, **updates)


def delete_entry(vault: Vault, entry_id: str) -> bool:
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
    vault_obj = load_vault(path, master_password)
    save_vault(target_path, vault_obj, master_password)


def import_encrypted(source_path: str, target_path: str, master_password: str) -> Vault:
    """
    Import an encrypted vault file to a new location.
    Returns the loaded vault object.
    """
    vault_obj = load_vault(source_path, master_password)
    save_vault(target_path, vault_obj, master_password)
    return vault_obj


def migrate_entry_to_v2(entry: Entry) -> Entry:
    """
    Migrate an entry from v1.x format to v2.x format.
    Adds missing fields with default values for backwards compatibility.

    Args:
        entry: Entry dict to migrate

    Returns:
        Migrated entry with all v2.x fields
    """
    # Add tags field if missing
    if 'tags' not in entry:
        entry['tags'] = []

    # Add pinned field if missing
    if 'pinned' not in entry:
        entry['pinned'] = False

    # Add password_history field if missing
    if 'password_history' not in entry:
        entry['password_history'] = []

    # Ensure type field exists (defaults to password)
    if 'type' not in entry:
        entry['type'] = 'password'

    return entry


def ensure_vault_compatibility(vault_obj: Vault) -> Vault:
    """
    Ensure vault is compatible with current version.
    Migrates all entries to latest format.

    Args:
        vault_obj: Vault to check and migrate

    Returns:
        Vault with all entries migrated to current format
    """
    for entry in vault_obj['entries']:
        migrate_entry_to_v2(entry)

    return vault_obj
