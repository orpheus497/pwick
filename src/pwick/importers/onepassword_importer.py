"""
1Password importer for pwick.

Supports importing from 1Password CSV export format.
"""

from __future__ import annotations

import csv

from .. import vault
from .csv_importer import ImportResult


def import_from_onepassword_csv(vault_obj: vault.Vault, file_path: str) -> ImportResult:
    """
    Import entries from 1Password CSV export.

    1Password CSV format typically has columns:
    Title, Website, Username, Password, Notes, Type, etc.

    Args:
        vault_obj: Vault to import into
        file_path: Path to 1Password CSV file

    Returns:
        ImportResult with success/error counts
    """
    result = ImportResult()

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    title = row.get("Title") or row.get("title") or ""
                    username = row.get("Username") or row.get("username") or ""
                    password = row.get("Password") or row.get("password") or ""
                    website = (
                        row.get("Website")
                        or row.get("website")
                        or row.get("URL")
                        or row.get("url")
                        or ""
                    )
                    notes = row.get("Notes") or row.get("notes") or ""
                    item_type = row.get("Type") or row.get("type") or ""

                    if not title:
                        result.add_error(row_num, "Missing title")
                        continue

                    # Combine website and notes
                    full_notes = []
                    if website:
                        full_notes.append(f"Website: {website}")
                    if notes:
                        full_notes.append(notes)

                    # Use type as tag
                    tags = [item_type] if item_type else []

                    entry_id = vault.add_entry(
                        vault_obj,
                        title=title,
                        username=username,
                        password=password,
                        notes="\n\n".join(full_notes),
                        tags=tags,
                        entry_type="password",
                    )

                    result.add_success(entry_id)

                except Exception as e:
                    result.add_error(row_num, str(e))

    except Exception as e:
        result.add_error(0, f"Failed to read 1Password CSV: {e}")

    return result
