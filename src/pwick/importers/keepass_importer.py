"""
KeePass importer for pwick.

Supports importing from KeePass CSV export format.
"""

from __future__ import annotations

import csv
from typing import List

from .. import vault
from .csv_importer import ImportResult


def import_from_keepass_csv(vault_obj: vault.Vault, file_path: str) -> ImportResult:
    """
    Import entries from KeePass CSV export.

    KeePass CSV format typically has columns:
    Group, Title, Username, Password, URL, Notes

    Args:
        vault_obj: Vault to import into
        file_path: Path to KeePass CSV file

    Returns:
        ImportResult with success/error counts
    """
    result = ImportResult()

    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    title = row.get('Title') or row.get('title') or ''
                    username = row.get('Username') or row.get('username') or ''
                    password = row.get('Password') or row.get('password') or ''
                    url = row.get('URL') or row.get('url') or ''
                    notes = row.get('Notes') or row.get('notes') or ''
                    group = row.get('Group') or row.get('group') or ''

                    if not title:
                        result.add_error(row_num, "Missing title")
                        continue

                    # Combine URL and notes
                    full_notes = []
                    if url:
                        full_notes.append(f"URL: {url}")
                    if notes:
                        full_notes.append(notes)

                    # Use group as tag
                    tags = [group] if group else []

                    entry_id = vault.add_entry(
                        vault_obj,
                        title=title,
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
        result.add_error(0, f"Failed to read KeePass CSV: {e}")

    return result
