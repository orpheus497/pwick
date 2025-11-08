"""
Bitwarden importer for pwick.

Supports importing from Bitwarden JSON and CSV export formats.
"""

from __future__ import annotations

import csv
import json
from typing import List

from .. import vault
from .csv_importer import ImportResult


def import_from_bitwarden_json(vault_obj: vault.Vault, file_path: str) -> ImportResult:
    """
    Import entries from Bitwarden JSON export.

    Args:
        vault_obj: Vault to import into
        file_path: Path to Bitwarden JSON export file

    Returns:
        ImportResult with success/error counts
    """
    result = ImportResult()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        items = data.get('items', [])

        for idx, item in enumerate(items, start=1):
            try:
                # Skip non-login items
                if item.get('type') != 1:  # 1 = login type in Bitwarden
                    continue

                name = item.get('name', '')
                login = item.get('login', {})
                notes = item.get('notes', '')
                folder = item.get('folderName') or item.get('folder')

                if not name:
                    result.add_error(idx, "Missing name")
                    continue

                username = login.get('username', '')
                password = login.get('password', '')
                uris = login.get('uris', [])

                # Combine URIs into notes
                full_notes = []
                if uris:
                    uri_texts = [uri.get('uri', '') for uri in uris if uri.get('uri')]
                    if uri_texts:
                        full_notes.append("URLs:\n" + '\n'.join(uri_texts))
                if notes:
                    full_notes.append(notes)

                # Use folder as tag
                tags = [folder] if folder else []

                entry_id = vault.add_entry(
                    vault_obj,
                    title=name,
                    username=username,
                    password=password,
                    notes='\n\n'.join(full_notes),
                    tags=tags,
                    entry_type='password'
                )

                result.add_success(entry_id)

            except Exception as e:
                result.add_error(idx, str(e))

    except Exception as e:
        result.add_error(0, f"Failed to read Bitwarden JSON: {e}")

    return result


def import_from_bitwarden_csv(vault_obj: vault.Vault, file_path: str) -> ImportResult:
    """
    Import entries from Bitwarden CSV export.

    Bitwarden CSV format has columns:
    folder, favorite, type, name, notes, fields, login_uri, login_username, login_password, login_totp

    Args:
        vault_obj: Vault to import into
        file_path: Path to Bitwarden CSV file

    Returns:
        ImportResult with success/error counts
    """
    result = ImportResult()

    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Skip non-login items
                    if row.get('type') != 'login':
                        continue

                    name = row.get('name', '')
                    username = row.get('login_username', '')
                    password = row.get('login_password', '')
                    uri = row.get('login_uri', '')
                    notes = row.get('notes', '')
                    folder = row.get('folder', '')

                    if not name:
                        result.add_error(row_num, "Missing name")
                        continue

                    # Combine URI and notes
                    full_notes = []
                    if uri:
                        full_notes.append(f"URL: {uri}")
                    if notes:
                        full_notes.append(notes)

                    # Use folder as tag
                    tags = [folder] if folder else []

                    entry_id = vault.add_entry(
                        vault_obj,
                        title=name,
                        username=username,
                        password=password,
                        notes='\n\n'.join(full_notes),
                        tags=tags,
                        entry_type='password'
                    )

                    result.add_success(entry_id)

                except Exception as e:
                    result.add_error(row_num, str(e))

    except Exception as e:
        result.add_error(0, f"Failed to read Bitwarden CSV: {e}")

    return result
