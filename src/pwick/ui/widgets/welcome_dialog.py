"""
Welcome dialog for pwick.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class WelcomeDialog(QDialog):
    """Initial welcome screen for creating, importing, or opening vaults."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pwick - Password Manager")
        self.setModal(True)
        self.resize(400, 300)
        
        self.result_action = None
        self.vault_path = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Welcome to pwick")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel("Your local-first password manager")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        create_btn = QPushButton("Create New Vault")
        create_btn.setObjectName("primaryButton")
        create_btn.clicked.connect(self._on_create)
        layout.addWidget(create_btn)
        
        import_btn = QPushButton("Import Existing Vault")
        import_btn.clicked.connect(self._on_import)
        layout.addWidget(import_btn)
        
        open_btn = QPushButton("Open Existing Vault")
        open_btn.clicked.connect(self._on_open)
        layout.addWidget(open_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _on_create(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Create New Vault", "", "Vault Files (*.vault);;All Files (*)"
        )
        if path:
            if not path.endswith('.vault'):
                path += '.vault'
            self.result_action = 'create'
            self.vault_path = path
            self.accept()
    
    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Vault File", "", "Encrypted Files (*.encrypted *.vault);;All Files (*)"
        )
        if path:
            self.result_action = 'import'
            self.vault_path = path
            self.accept()
    
    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Vault", "", "Vault Files (*.vault);;All Files (*)"
        )
        if path:
            self.result_action = 'open'
            self.vault_path = path
            self.accept()
