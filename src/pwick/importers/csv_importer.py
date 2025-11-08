"""
Generic CSV importer for pwick.

Handles importing from generic CSV files with flexible column mapping.
"""

from __future__ import annotations

import csv
from typing import List, Dict, Optional, Tuple

from .. import vault


class ImportResult:
    """Result of an import operation."""

    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.errors: List[Tuple[int, str]] = []
        self.imported_entries: List[str] = []

    def add_success(self, entry_id: str):
        """Record a successful import."""
        self.success_count += 1
        self.imported_entries.append(entry_id)

    def add_error(self, row_num: int, error_msg: str):
        """Record an import error."""
        self.error_count += 1
        self.errors.append((row_num, error_msg))

    def __str__(self) -> str:
        return (
            f"Import complete: {self.success_count} succeeded, "
            f"{self.error_count} failed"
        )


def detect_csv_format(file_path: str) -> Optional[str]:
    """
    Detect the CSV format by examining headers.

    Args:
        file_path: Path to CSV file

    Returns:
        Format name ("keepass", "bitwarden", "lastpass", "1password", "generic") or None
    """
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = [h.lower() if h else "" for h in reader.fieldnames or []]

            # KeePass format
            if "group" in headers and "title" in headers and "username" in headers:
                return "keepass"

            # Bitwarden format
            if "folder" in headers and "type" in headers and "name" in headers:
                return "bitwarden"

            # LastPass format
            if (
                "url" in headers
                and "username" in headers
                and "password" in headers
                and "extra" in headers
            ):
                return "lastpass"

            # 1Password format
            if "title" in headers and "website" in headers and "username" in headers:
                return "1password"

            # Generic format (has title/username/password)
            if "title" in headers or "name" in headers:
                return "generic"

    except Exception:
        pass

    return None


def import_from_csv(
    vault_obj: vault.Vault, file_path: str, column_map: Optional[Dict[str, str]] = None
) -> ImportResult:
    """
    Import entries from a generic CSV file.

    Args:
        vault_obj: Vault to import into
        file_path: Path to CSV file
        column_map: Optional mapping of CSV columns to entry fields
                   e.g., {"Title": "title", "User": "username", ...}

    Returns:
        ImportResult with success/error counts and details
    """
    result = ImportResult()

    # Default column mapping (case-insensitive)
    default_map = {
        "title": "title",
        "name": "title",
        "username": "username",
        "user": "username",
        "login": "username",
        "password": "password",
        "pass": "password",
        "notes": "notes",
        "note": "notes",
        "comment": "notes",
        "comments": "notes",
        "url": "notes",  # Append URL to notes
        "website": "notes",
        "tags": "tags",
        "tag": "tags",
    }

    if column_map:
        # Merge user-provided mapping
        default_map.update(column_map)

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            # Read CSV with flexible dialect detection
            sample = f.read(8192)
            f.seek(0)

            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel

            reader = csv.DictReader(f, dialect=dialect)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                try:
                    # Extract fields using column mapping
                    entry_data = _extract_entry_data(row, default_map)

                    if not entry_data.get("title"):
                        result.add_error(row_num, "Missing title/name field")
                        continue

                    # Parse tags if present
                    tags = []
                    if entry_data.get("tags"):
                        tag_str = entry_data["tags"]
                        # Split on common delimiters
                        for delimiter in [",", ";", "|"]:
                            if delimiter in tag_str:
                                tags = [t.strip() for t in tag_str.split(delimiter)]
                                break
                        if not tags:
                            tags = [tag_str.strip()]

                    # Add entry to vault
                    entry_id = vault.add_entry(
                        vault_obj,
                        title=entry_data.get("title", ""),
                        username=entry_data.get("username", ""),
                        password=entry_data.get("password", ""),
                        notes=entry_data.get("notes", ""),
                        tags=tags,
                        entry_type="password",
                    )

                    result.add_success(entry_id)

                except Exception as e:
                    result.add_error(row_num, str(e))

    except Exception as e:
        result.add_error(0, f"Failed to read CSV file: {e}")

    return result


def _extract_entry_data(
    row: Dict[str, str], column_map: Dict[str, str]
) -> Dict[str, str]:
    """
    Extract entry data from a CSV row using column mapping.

    Args:
        row: CSV row as dictionary
        column_map: Mapping of CSV columns to entry fields

    Returns:
        Dictionary with entry fields
    """
    entry_data: Dict[str, str] = {
        "title": "",
        "username": "",
        "password": "",
        "notes": "",
        "tags": "",
    }

    notes_parts = []

    for csv_col, csv_val in row.items():
        if not csv_col or not csv_val:
            continue

        csv_col_lower = csv_col.lower().strip()

        # Check if this column maps to a standard field
        if csv_col_lower in column_map:
            target_field = column_map[csv_col_lower]

            if target_field in ["title", "username", "password", "tags"]:
                # Direct field mapping
                if not entry_data[target_field]:  # Don't overwrite if already set
                    entry_data[target_field] = csv_val.strip()
            elif target_field == "notes":
                # Append to notes
                notes_parts.append(f"{csv_col}: {csv_val.strip()}")
        else:
            # Unknown column - append to notes
            notes_parts.append(f"{csv_col}: {csv_val.strip()}")

    # Combine notes parts
    if notes_parts:
        if entry_data["notes"]:
            entry_data["notes"] += "\n\n" + "\n".join(notes_parts)
        else:
            entry_data["notes"] = "\n".join(notes_parts)

    return entry_data


def export_to_csv(
    vault_obj: vault.Vault, file_path: str, include_passwords: bool = True
) -> int:
    """
    Export vault entries to CSV format.

    Args:
        vault_obj: Vault to export from
        file_path: Path to save CSV file
        include_passwords: Whether to include passwords (default: True)

    Returns:
        Number of entries exported
    """
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "title",
            "username",
            "password",
            "notes",
            "tags",
            "created_at",
            "updated_at",
        ]

        if not include_passwords:
            fieldnames.remove("password")

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for entry in vault_obj["entries"]:
            if entry.get("type", "password") == "password":
                row_data = {
                    "title": entry.get("title", ""),
                    "username": entry.get("username", ""),
                    "notes": entry.get("notes", ""),
                    "tags": ", ".join(entry.get("tags", [])),
                    "created_at": entry.get("created_at", ""),
                    "updated_at": entry.get("updated_at", ""),
                }

                if include_passwords:
                    row_data["password"] = entry.get("password", "")

                writer.writerow(row_data)
                count += 1

    return count
