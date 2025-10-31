"""
Master password dialog for pwick.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from .password_strength_widget import PasswordStrengthWidget


class MasterPasswordDialog(QDialog):
    """Dialog for entering master password."""
    
    def __init__(self, confirm_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Master Password")
        self.setModal(True)
        self.confirm_mode = confirm_mode
        self.password = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        label = QLabel("Enter Master Password:" if not self.confirm_mode 
                      else "Create Master Password:")
        layout.addWidget(label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Master Password")
        layout.addWidget(self.password_input)

        # Add password strength widget in confirm mode
        if self.confirm_mode:
            self.strength_widget = PasswordStrengthWidget()
            self.password_input.textChanged.connect(self.strength_widget.update_password)
            layout.addWidget(self.strength_widget)

            confirm_label = QLabel("Confirm Master Password:")
            layout.addWidget(confirm_label)

            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setPlaceholderText("Confirm Password")
            layout.addWidget(self.confirm_input)
        
        warning = QLabel(
            "⚠️ WARNING: Your master password cannot be recovered. "
            "If you forget it, your data will be lost forever."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #c62828; font-size: 10px;")
        layout.addWidget(warning)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _on_ok(self):
        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return

        if self.confirm_mode:
            # Validate password strength
            if not self.strength_widget.is_strong_enough(minimum_score=3):
                reply = QMessageBox.warning(
                    self,
                    "Weak Password",
                    "Your master password does not meet the recommended strength requirements.\n\n"
                    "A weak master password undermines the strong encryption used to protect your vault.\n\n"
                    "Recommendation: Use at least 12 characters with a mix of letters, numbers, and symbols.\n\n"
                    "Do you want to proceed anyway? (NOT RECOMMENDED)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return

            # Check minimum length (absolute requirement)
            if len(password) < 8:
                QMessageBox.critical(
                    self,
                    "Password Too Short",
                    "Master password must be at least 8 characters long.\n"
                    "For your security, please choose a longer password."
                )
                return

            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(self, "Error", "Passwords do not match.")
                return

        self.password = password
        self.accept()
