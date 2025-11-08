"""
Security audit dialog for pwick.

Analyzes the vault for security issues including:
- Duplicate passwords across entries
- Weak passwords that should be upgraded
"""

from typing import List, Dict
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
)
from PySide6.QtCore import Qt

try:
    import zxcvbn

    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False


class SecurityAuditDialog(QDialog):
    """
    Dialog that displays security audit results for the vault.

    Shows two tabs:
    - Duplicate Passwords: Entries using the same password
    - Weak Passwords: Entries with passwords below strength threshold
    """

    def __init__(self, vault_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Audit")
        self.setModal(True)
        self.resize(700, 500)

        self.vault_data = vault_data
        self.duplicate_groups = []
        self.weak_entries = []

        self._run_audit()
        self._setup_ui()

    def _run_audit(self):
        """Run security audit on vault data."""
        # Find duplicate passwords
        password_map: Dict[str, List[Dict]] = {}

        for entry in self.vault_data["entries"]:
            # Only audit password entries (not notes)
            if entry.get("type", "password") != "password":
                continue

            password = entry.get("password", "")
            if not password:
                continue

            if password not in password_map:
                password_map[password] = []
            password_map[password].append(entry)

        # Keep only passwords used by multiple entries
        self.duplicate_groups = [
            entries for entries in password_map.values() if len(entries) > 1
        ]

        # Find weak passwords (zxcvbn score < 3)
        self.weak_entries = []

        if ZXCVBN_AVAILABLE:
            for entry in self.vault_data["entries"]:
                if entry.get("type", "password") != "password":
                    continue

                password = entry.get("password", "")
                if not password:
                    continue

                result = zxcvbn.zxcvbn(password)
                if result["score"] < 3:  # Fair or below
                    self.weak_entries.append(
                        {
                            "entry": entry,
                            "score": result["score"],
                            "warning": result.get("feedback", {}).get("warning", ""),
                            "suggestions": result.get("feedback", {}).get(
                                "suggestions", []
                            ),
                        }
                    )
        else:
            # Fallback: Simple length-based check
            for entry in self.vault_data["entries"]:
                if entry.get("type", "password") != "password":
                    continue

                password = entry.get("password", "")
                if password and len(password) < 12:
                    self.weak_entries.append(
                        {
                            "entry": entry,
                            "score": 1,
                            "warning": "Password is too short",
                            "suggestions": ["Use at least 12 characters"],
                        }
                    )

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout()

        # Summary at top
        summary_label = QLabel(self._get_summary_text())
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet(
            "padding: 10px; background-color: #2d2d2d; border-radius: 4px;"
        )
        layout.addWidget(summary_label)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(
            self._create_duplicates_tab(),
            f"Duplicate Passwords ({len(self.duplicate_groups)})",
        )
        self.tabs.addTab(
            self._create_weak_passwords_tab(),
            f"Weak Passwords ({len(self.weak_entries)})",
        )
        layout.addWidget(self.tabs)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("primaryButton")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _get_summary_text(self) -> str:
        """Generate summary text for audit results."""
        total_issues = len(self.duplicate_groups) + len(self.weak_entries)

        if total_issues == 0:
            return "✓ No security issues found! Your passwords are in good shape."

        parts = ["⚠️ Security audit found the following issues:"]

        if self.duplicate_groups:
            dup_count = sum(len(group) for group in self.duplicate_groups)
            parts.append(
                f"• {dup_count} entries using {len(self.duplicate_groups)} duplicate password(s)"
            )

        if self.weak_entries:
            parts.append(
                f"• {len(self.weak_entries)} weak password(s) that should be upgraded"
            )

        parts.append(
            "\nReview the tabs below for details and take action to improve your security."
        )

        return "\n".join(parts)

    def _create_duplicates_tab(self) -> QWidget:
        """Create the Duplicate Passwords tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        if not self.duplicate_groups:
            no_issues = QLabel(
                "✓ No duplicate passwords found!\n\n"
                "Each of your entries uses a unique password, which is excellent for security."
            )
            no_issues.setAlignment(Qt.AlignCenter)
            no_issues.setStyleSheet("color: #7cb342; font-size: 14px; padding: 20px;")
            layout.addWidget(no_issues)
        else:
            help_text = QLabel(
                "The following passwords are used by multiple entries.\n"
                "Using the same password across different accounts is a security risk:\n"
                "if one account is compromised, all accounts using that password are at risk.\n\n"
                "Recommendation: Generate unique passwords for each entry."
            )
            help_text.setWordWrap(True)
            help_text.setStyleSheet("color: #fbc02d; padding: 5px;")
            layout.addWidget(help_text)

            # List duplicate groups
            for i, group in enumerate(self.duplicate_groups, 1):
                group_box = QGroupBox(f"Duplicate Group {i} ({len(group)} entries)")
                group_layout = QVBoxLayout()

                list_widget = QListWidget()
                for entry in group:
                    item_text = f"{entry['title']}"
                    if entry.get("username"):
                        item_text += f" (username: {entry['username']})"
                    list_widget.addItem(item_text)

                group_layout.addWidget(list_widget)
                group_box.setLayout(group_layout)
                layout.addWidget(group_box)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_weak_passwords_tab(self) -> QWidget:
        """Create the Weak Passwords tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        if not self.weak_entries:
            no_issues = QLabel(
                "✓ No weak passwords found!\n\n"
                "All your passwords meet good strength standards."
            )
            no_issues.setAlignment(Qt.AlignCenter)
            no_issues.setStyleSheet("color: #7cb342; font-size: 14px; padding: 20px;")
            layout.addWidget(no_issues)
        else:
            help_text = QLabel(
                "The following entries have passwords that don't meet good strength standards.\n"
                "Weak passwords are vulnerable to guessing and brute-force attacks.\n\n"
                "Recommendation: Use the password generator to create strong, random passwords."
            )
            help_text.setWordWrap(True)
            help_text.setStyleSheet("color: #fbc02d; padding: 5px;")
            layout.addWidget(help_text)

            # List weak passwords
            list_widget = QListWidget()

            for weak in self.weak_entries:
                entry = weak["entry"]
                score = weak["score"]
                warning = weak["warning"]

                # Create display text
                strength_text = (
                    ["Very Weak", "Weak", "Fair"][score] if score < 3 else "Fair"
                )
                item_text = f"{entry['title']}"
                if entry.get("username"):
                    item_text += f" ({entry['username']})"
                item_text += f" - Strength: {strength_text}"

                if warning:
                    item_text += f"\n  ⚠ {warning}"

                suggestions = weak.get("suggestions", [])
                if suggestions:
                    item_text += "\n  💡 " + "; ".join(suggestions)

                item = QListWidgetItem(item_text)

                # Color code by severity
                if score == 0:
                    item.setForeground(Qt.red)
                elif score == 1:
                    item.setForeground(Qt.yellow)
                else:
                    item.setForeground(Qt.cyan)

                list_widget.addItem(item)

            layout.addWidget(list_widget)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def get_duplicate_count(self) -> int:
        """Get number of duplicate password groups found."""
        return len(self.duplicate_groups)

    def get_weak_count(self) -> int:
        """Get number of weak passwords found."""
        return len(self.weak_entries)

    def has_issues(self) -> bool:
        """Check if any security issues were found."""
        return len(self.duplicate_groups) > 0 or len(self.weak_entries) > 0
