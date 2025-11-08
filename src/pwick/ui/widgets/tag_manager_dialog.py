"""
pwick.ui.dialogs.tag_manager_dialog - Centralized tag management dialog.

Allows users to view, rename, merge, and delete tags across all vault entries.
"""

from typing import Optional, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QMessageBox, QInputDialog
)

from ... import vault


class TagManagerDialog(QDialog):
    """Dialog for managing tags across the entire vault."""

    def __init__(self, vault_data: dict, parent=None):
        super().__init__(parent)
        self.vault_data = vault_data
        self.tag_usage: Dict[str, int] = {}
        self.modified = False

        self.setWindowTitle("Tag Manager")
        self.setMinimumSize(500, 400)

        self._init_ui()
        self._refresh_tag_list()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Manage Tags")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        info = QLabel("View and manage tags used in your vault entries.")
        layout.addWidget(info)

        # Tag list
        self.tag_list = QListWidget()
        self.tag_list.itemSelectionChanged.connect(self._on_tag_selection_changed)
        layout.addWidget(self.tag_list)

        # Buttons
        button_layout = QHBoxLayout()

        self.rename_btn = QPushButton("Rename Tag")
        self.rename_btn.clicked.connect(self._rename_tag)
        self.rename_btn.setEnabled(False)
        button_layout.addWidget(self.rename_btn)

        self.merge_btn = QPushButton("Merge Tags")
        self.merge_btn.clicked.connect(self._merge_tags)
        self.merge_btn.setEnabled(False)
        button_layout.addWidget(self.merge_btn)

        self.delete_btn = QPushButton("Delete Tag")
        self.delete_btn.clicked.connect(self._delete_tag)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)

        layout.addLayout(close_layout)

    def _refresh_tag_list(self):
        """Refresh the tag list with current usage counts."""
        self.tag_list.clear()
        self.tag_usage.clear()

        # Count tag usage across all entries
        for entry in self.vault_data['entries']:
            tags = entry.get('tags', [])
            for tag in tags:
                self.tag_usage[tag] = self.tag_usage.get(tag, 0) + 1

        # Sort tags alphabetically
        sorted_tags = sorted(self.tag_usage.keys())

        # Add tags to list with usage count
        for tag in sorted_tags:
            count = self.tag_usage[tag]
            plural = "entry" if count == 1 else "entries"
            item = QListWidgetItem(f"{tag} ({count} {plural})")
            item.setData(Qt.UserRole, tag)
            self.tag_list.addItem(item)

        # Show message if no tags
        if not sorted_tags:
            item = QListWidgetItem("No tags found in vault")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.tag_list.addItem(item)

    def _on_tag_selection_changed(self):
        """Enable/disable buttons based on selection."""
        has_selection = len(self.tag_list.selectedItems()) > 0
        has_multiple = len(self.tag_list.selectedItems()) > 1

        self.rename_btn.setEnabled(has_selection and not has_multiple)
        self.merge_btn.setEnabled(has_multiple)
        self.delete_btn.setEnabled(has_selection)

    def _rename_tag(self):
        """Rename the selected tag across all entries."""
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            return

        old_tag = selected_items[0].data(Qt.UserRole)
        if not old_tag:
            return

        new_tag, ok = QInputDialog.getText(
            self,
            "Rename Tag",
            f"Rename tag '{old_tag}' to:",
            text=old_tag
        )

        if not ok or not new_tag or new_tag == old_tag:
            return

        # Check if new tag already exists
        if new_tag in self.tag_usage:
            reply = QMessageBox.question(
                self,
                "Tag Exists",
                f"Tag '{new_tag}' already exists. Do you want to merge '{old_tag}' into '{new_tag}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Rename tag in all entries
        for entry in self.vault_data['entries']:
            tags = entry.get('tags', [])
            if old_tag in tags:
                tags.remove(old_tag)
                if new_tag not in tags:
                    tags.append(new_tag)

        self.modified = True
        self._refresh_tag_list()

        QMessageBox.information(
            self,
            "Success",
            f"Renamed tag '{old_tag}' to '{new_tag}' in {self.tag_usage.get(old_tag, 0)} entries."
        )

    def _merge_tags(self):
        """Merge multiple selected tags into one."""
        selected_items = self.tag_list.selectedItems()
        if len(selected_items) < 2:
            return

        # Get all selected tag names
        tags_to_merge = [item.data(Qt.UserRole) for item in selected_items]
        tags_to_merge = [t for t in tags_to_merge if t]  # Filter out None

        if not tags_to_merge:
            return

        # Ask which tag to keep
        keep_tag, ok = QInputDialog.getItem(
            self,
            "Merge Tags",
            f"Merge {len(tags_to_merge)} tags into:",
            tags_to_merge,
            0,
            True
        )

        if not ok or not keep_tag:
            return

        # Confirm merge
        other_tags = [t for t in tags_to_merge if t != keep_tag]
        reply = QMessageBox.question(
            self,
            "Confirm Merge",
            f"Merge tags {', '.join(f\"'{t}\"\" for t in other_tags)} into '{keep_tag}'?\n\n"
            f"This will remove the other tags and replace them with '{keep_tag}'.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        # Merge tags in all entries
        affected_entries = 0
        for entry in self.vault_data['entries']:
            tags = entry.get('tags', [])
            modified = False

            for tag in tags_to_merge:
                if tag in tags and tag != keep_tag:
                    tags.remove(tag)
                    modified = True

            if modified and keep_tag not in tags:
                tags.append(keep_tag)
                affected_entries += 1
            elif modified:
                affected_entries += 1

        self.modified = True
        self._refresh_tag_list()

        QMessageBox.information(
            self,
            "Success",
            f"Merged {len(other_tags)} tags into '{keep_tag}' across {affected_entries} entries."
        )

    def _delete_tag(self):
        """Delete the selected tag(s) from all entries."""
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            return

        # Get all selected tag names
        tags_to_delete = [item.data(Qt.UserRole) for item in selected_items]
        tags_to_delete = [t for t in tags_to_delete if t]  # Filter out None

        if not tags_to_delete:
            return

        # Confirm deletion
        if len(tags_to_delete) == 1:
            tag = tags_to_delete[0]
            count = self.tag_usage.get(tag, 0)
            message = f"Delete tag '{tag}' from {count} {'entry' if count == 1 else 'entries'}?"
        else:
            total_entries = sum(self.tag_usage.get(t, 0) for t in tags_to_delete)
            message = f"Delete {len(tags_to_delete)} tags from {total_entries} entries?"

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            message,
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        # Delete tags from all entries
        affected_entries = 0
        for entry in self.vault_data['entries']:
            tags = entry.get('tags', [])
            original_count = len(tags)

            for tag in tags_to_delete:
                if tag in tags:
                    tags.remove(tag)

            if len(tags) < original_count:
                affected_entries += 1

        self.modified = True
        self._refresh_tag_list()

        if len(tags_to_delete) == 1:
            QMessageBox.information(
                self,
                "Success",
                f"Deleted tag '{tags_to_delete[0]}' from {affected_entries} entries."
            )
        else:
            QMessageBox.information(
                self,
                "Success",
                f"Deleted {len(tags_to_delete)} tags from {affected_entries} entries."
            )
