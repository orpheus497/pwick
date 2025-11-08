"""
Import functionality for pwick.

Supports importing from various password manager formats:
- Generic CSV
- KeePass CSV/XML
- Bitwarden JSON/CSV
- 1Password CSV
- LastPass CSV
"""

from __future__ import annotations

from .csv_importer import import_from_csv, detect_csv_format
from .keepass_importer import import_from_keepass_csv
from .bitwarden_importer import import_from_bitwarden_json, import_from_bitwarden_csv
from .lastpass_importer import import_from_lastpass_csv
from .onepassword_importer import import_from_onepassword_csv

__all__ = [
    "import_from_csv",
    "detect_csv_format",
    "import_from_keepass_csv",
    "import_from_bitwarden_json",
    "import_from_bitwarden_csv",
    "import_from_lastpass_csv",
    "import_from_onepassword_csv",
]
