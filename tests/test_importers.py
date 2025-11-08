"""
Tests for pwick importers module.

Tests cover:
- CSV format detection
- KeePass CSV import
- Bitwarden JSON and CSV import
- LastPass CSV import
- 1Password CSV import
- Generic CSV import with custom mapping
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pwick.importers.csv_importer import (
    ImportResult,
    detect_csv_format,
    import_from_csv,
)
from pwick.importers.keepass_importer import import_from_keepass_csv
from pwick.importers.bitwarden_importer import (
    import_from_bitwarden_json,
    import_from_bitwarden_csv,
)
from pwick.importers.lastpass_importer import import_from_lastpass_csv
from pwick.importers.onepassword_importer import import_from_onepassword_csv


class TestImportResult:
    """Test ImportResult class."""

    def test_import_result_initialization(self):
        """Test that ImportResult initializes correctly."""
        result = ImportResult()
        assert result.success_count == 0
        assert result.error_count == 0
        assert result.errors == []

    def test_add_success(self):
        """Test adding successful imports."""
        result = ImportResult()
        result.add_success("entry-123")
        assert result.success_count == 1
        assert len(result.successful_entry_ids) == 1

    def test_add_error(self):
        """Test adding errors."""
        result = ImportResult()
        result.add_error(1, "Test error")
        assert result.error_count == 1
        assert len(result.errors) == 1
        assert result.errors[0] == (1, "Test error")

    def test_get_summary(self):
        """Test getting result summary."""
        result = ImportResult()
        result.add_success("entry-1")
        result.add_success("entry-2")
        result.add_error(3, "Failed to import")

        summary = result.get_summary()
        assert "2 successful" in summary
        assert "1 failed" in summary


class TestCSVFormatDetection:
    """Test CSV format detection."""

    def test_detect_keepass_format(self, tmp_path):
        """Test detection of KeePass CSV format."""
        csv_file = tmp_path / "keepass.csv"
        csv_file.write_text(
            "Group,Title,Username,Password,URL,Notes\n"
            "Work,Gmail,user@example.com,pass123,https://gmail.com,My email\n"
        )

        format_type = detect_csv_format(str(csv_file))
        assert format_type == "keepass"

    def test_detect_bitwarden_format(self, tmp_path):
        """Test detection of Bitwarden CSV format."""
        csv_file = tmp_path / "bitwarden.csv"
        csv_file.write_text(
            "folder,favorite,type,name,notes,fields,login_uri,login_username,login_password,login_totp\n"
            "Work,0,login,Gmail,Notes,,,user@example.com,pass123,\n"
        )

        format_type = detect_csv_format(str(csv_file))
        assert format_type == "bitwarden"

    def test_detect_lastpass_format(self, tmp_path):
        """Test detection of LastPass CSV format."""
        csv_file = tmp_path / "lastpass.csv"
        csv_file.write_text(
            "url,username,password,extra,name,grouping,fav\n"
            "https://gmail.com,user@example.com,pass123,,Gmail,Work,0\n"
        )

        format_type = detect_csv_format(str(csv_file))
        assert format_type == "lastpass"

    def test_detect_onepassword_format(self, tmp_path):
        """Test detection of 1Password CSV format."""
        csv_file = tmp_path / "1password.csv"
        csv_file.write_text(
            "Title,Website,Username,Password,Notes,Type\n"
            "Gmail,https://gmail.com,user@example.com,pass123,My email,Login\n"
        )

        format_type = detect_csv_format(str(csv_file))
        assert format_type == "1password"

    def test_detect_generic_format(self, tmp_path):
        """Test detection falls back to generic for unknown formats."""
        csv_file = tmp_path / "unknown.csv"
        csv_file.write_text("col1,col2,col3\n" "data1,data2,data3\n")

        format_type = detect_csv_format(str(csv_file))
        assert format_type == "generic"


class TestKeePassImporter:
    """Test KeePass CSV importer."""

    def test_import_keepass_csv(self, tmp_path):
        """Test importing from KeePass CSV."""
        csv_file = tmp_path / "keepass.csv"
        csv_file.write_text(
            "Group,Title,Username,Password,URL,Notes\n"
            "Work,Gmail,user@example.com,pass123,https://gmail.com,My email account\n"
            "Personal,Facebook,user@fb.com,fbpass,https://facebook.com,Social media\n"
        )

        mock_vault = Mock()
        mock_vault.data = {"entries": {}}

        # Mock the vault.add_entry function
        entry_counter = [0]

        def mock_add_entry(
            vault_obj, title, username, password, notes, tags, entry_type
        ):
            entry_counter[0] += 1
            return f"entry-{entry_counter[0]}"

        import pwick.importers.keepass_importer as keepass_module

        with pytest.MonkeyPatch.context() as m:
            m.setattr(keepass_module.vault, "add_entry", mock_add_entry)

            result = import_from_keepass_csv(mock_vault, str(csv_file))

            assert result.success_count == 2
            assert result.error_count == 0

    def test_import_keepass_csv_missing_title(self, tmp_path):
        """Test importing KeePass CSV with missing title."""
        csv_file = tmp_path / "keepass_bad.csv"
        csv_file.write_text(
            "Group,Title,Username,Password,URL,Notes\n"
            "Work,,user@example.com,pass123,https://gmail.com,Missing title\n"
        )

        mock_vault = Mock()

        result = import_from_keepass_csv(mock_vault, str(csv_file))

        assert result.success_count == 0
        assert result.error_count == 1


class TestBitwardenImporter:
    """Test Bitwarden importers."""

    def test_import_bitwarden_json(self, tmp_path):
        """Test importing from Bitwarden JSON."""
        json_file = tmp_path / "bitwarden.json"
        data = {
            "items": [
                {
                    "type": 1,  # Login type
                    "name": "Gmail",
                    "login": {
                        "username": "user@example.com",
                        "password": "pass123",
                        "uris": [{"uri": "https://gmail.com"}],
                    },
                    "notes": "My email",
                    "folderName": "Work",
                }
            ]
        }
        json_file.write_text(json.dumps(data))

        mock_vault = Mock()

        def mock_add_entry(
            vault_obj, title, username, password, notes, tags, entry_type
        ):
            return "entry-1"

        import pwick.importers.bitwarden_importer as bitwarden_module

        with pytest.MonkeyPatch.context() as m:
            m.setattr(bitwarden_module.vault, "add_entry", mock_add_entry)

            result = import_from_bitwarden_json(mock_vault, str(json_file))

            assert result.success_count == 1
            assert result.error_count == 0

    def test_import_bitwarden_csv(self, tmp_path):
        """Test importing from Bitwarden CSV."""
        csv_file = tmp_path / "bitwarden.csv"
        csv_file.write_text(
            "folder,favorite,type,name,notes,fields,login_uri,login_username,login_password,login_totp\n"
            "Work,0,login,Gmail,My email,,https://gmail.com,user@example.com,pass123,\n"
        )

        mock_vault = Mock()

        def mock_add_entry(
            vault_obj, title, username, password, notes, tags, entry_type
        ):
            return "entry-1"

        import pwick.importers.bitwarden_importer as bitwarden_module

        with pytest.MonkeyPatch.context() as m:
            m.setattr(bitwarden_module.vault, "add_entry", mock_add_entry)

            result = import_from_bitwarden_csv(mock_vault, str(csv_file))

            assert result.success_count == 1
            assert result.error_count == 0


class TestLastPassImporter:
    """Test LastPass CSV importer."""

    def test_import_lastpass_csv(self, tmp_path):
        """Test importing from LastPass CSV."""
        csv_file = tmp_path / "lastpass.csv"
        csv_file.write_text(
            "url,username,password,extra,name,grouping,fav\n"
            "https://gmail.com,user@example.com,pass123,My notes,Gmail,Work,0\n"
        )

        mock_vault = Mock()

        def mock_add_entry(
            vault_obj, title, username, password, notes, tags, entry_type
        ):
            return "entry-1"

        import pwick.importers.lastpass_importer as lastpass_module

        with pytest.MonkeyPatch.context() as m:
            m.setattr(lastpass_module.vault, "add_entry", mock_add_entry)

            result = import_from_lastpass_csv(mock_vault, str(csv_file))

            assert result.success_count == 1
            assert result.error_count == 0


class Test1PasswordImporter:
    """Test 1Password CSV importer."""

    def test_import_onepassword_csv(self, tmp_path):
        """Test importing from 1Password CSV."""
        csv_file = tmp_path / "1password.csv"
        csv_file.write_text(
            "Title,Website,Username,Password,Notes,Type\n"
            "Gmail,https://gmail.com,user@example.com,pass123,My email,Login\n"
        )

        mock_vault = Mock()

        def mock_add_entry(
            vault_obj, title, username, password, notes, tags, entry_type
        ):
            return "entry-1"

        import pwick.importers.onepassword_importer as onepassword_module

        with pytest.MonkeyPatch.context() as m:
            m.setattr(onepassword_module.vault, "add_entry", mock_add_entry)

            result = import_from_onepassword_csv(mock_vault, str(csv_file))

            assert result.success_count == 1
            assert result.error_count == 0


class TestGenericCSVImporter:
    """Test generic CSV importer with custom mapping."""

    def test_import_generic_csv_with_mapping(self, tmp_path):
        """Test importing generic CSV with custom column mapping."""
        csv_file = tmp_path / "custom.csv"
        csv_file.write_text(
            "site,user,pass,comment\n" "Gmail,user@example.com,pass123,My email\n"
        )

        mock_vault = Mock()

        def mock_add_entry(
            vault_obj, title, username, password, notes, tags, entry_type
        ):
            return "entry-1"

        column_map = {
            "title": "site",
            "username": "user",
            "password": "pass",
            "notes": "comment",
        }

        import pwick.importers.csv_importer as csv_module

        with pytest.MonkeyPatch.context() as m:
            m.setattr(csv_module.vault, "add_entry", mock_add_entry)

            result = import_from_csv(mock_vault, str(csv_file), column_map)

            assert result.success_count == 1
            assert result.error_count == 0


class TestImportErrorHandling:
    """Test error handling in importers."""

    def test_import_nonexistent_file(self):
        """Test importing from nonexistent file."""
        mock_vault = Mock()

        result = import_from_keepass_csv(mock_vault, "/nonexistent/file.csv")

        assert result.success_count == 0
        assert result.error_count >= 1

    def test_import_invalid_json(self, tmp_path):
        """Test importing invalid JSON file."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{invalid json content")

        mock_vault = Mock()

        result = import_from_bitwarden_json(mock_vault, str(json_file))

        assert result.success_count == 0
        assert result.error_count >= 1

    def test_import_empty_csv(self, tmp_path):
        """Test importing empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("Group,Title,Username,Password,URL,Notes\n")

        mock_vault = Mock()

        result = import_from_keepass_csv(mock_vault, str(csv_file))

        assert result.success_count == 0
        assert result.error_count == 0  # No errors, just no data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
