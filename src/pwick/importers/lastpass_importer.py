"""
LastPass importer for pwick.

Supports importing from LastPass CSV export format.
"""

from __future__ import annotations

import csv

from .. import vault
from .csv_importer import ImportResult


def import_from_lastpass_csv(vault_obj: vault.Vault, file_path: str) -> ImportResult:
    """
    Import entries from LastPass CSV export.

    LastPass CSV format has columns:
    url, username, password, extra, name, grouping, fav

    Args:
        vault_obj: Vault to import into
        file_path: Path to LastPass CSV file

    Returns:
        ImportResult with success/error counts
    """
    result = ImportResult()

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    name = row.get("name", "")
                    username = row.get("username", "")
                    password = row.get("password", "")
                    url = row.get("url", "")
                    extra = row.get("extra", "")
                    grouping = row.get("grouping", "")

                    if not name:
                        result.add_error(row_num, "Missing name")
                        continue

                    # Combine URL and extra notes
                    full_notes = []
                    if url:
                        full_notes.append(f"URL: {url}")
                    if extra:
                        full_notes.append(extra)

                    # Use grouping as tag
                    tags = [grouping] if grouping else []

                    entry_id = vault.add_entry(
                        vault_obj,
                        title=name,
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
        result.add_error(0, f"Failed to read LastPass CSV: {e}")

    return result
