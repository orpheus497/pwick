"""
pwick.ui.themes - Theme management for pwick UI.

Provides dark and light theme stylesheets for the application,
with a function to get the appropriate theme based on user settings.
"""

from typing import Literal

ThemeName = Literal["dark", "light"]


# Dark theme stylesheet with black, grey, white, and red accents
DARK_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

QLabel {
    color: #e0e0e0;
    font-size: 12px;
}

QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #c62828;
}

QPushButton:pressed {
    background-color: #c62828;
}

QPushButton#primaryButton {
    background-color: #c62828;
    border: 1px solid #b71c1c;
}

QPushButton#primaryButton:hover {
    background-color: #d32f2f;
}

QPushButton#primaryButton:pressed {
    background-color: #b71c1c;
}

QPushButton:disabled {
    background-color: #1a1a1a;
    color: #666666;
    border: 1px solid #2d2d2d;
}

QLineEdit, QTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #c62828;
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: #1a1a1a;
    color: #666666;
}

QListWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 4px;
    font-size: 12px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #404040;
}

QListWidget::item:selected {
    background-color: #c62828;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QGroupBox {
    border: 1px solid #404040;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    color: #e0e0e0;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
}

QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #404040;
    border-radius: 3px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #c62828;
    border: 1px solid #b71c1c;
}

QMessageBox {
    background-color: #1a1a1a;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

QTabWidget::pane {
    border: 1px solid #404040;
    border-radius: 4px;
    background-color: #1a1a1a;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #c62828;
    border-bottom-color: #c62828;
}

QTabBar::tab:hover {
    background-color: #3d3d3d;
}

QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
}

QComboBox:hover {
    border: 1px solid #c62828;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    selection-background-color: #c62828;
    border: 1px solid #404040;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #c62828;
    border: 1px solid #b71c1c;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #d32f2f;
}

QSpinBox, QDoubleSpinBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #c62828;
}

QProgressBar {
    border: 1px solid #404040;
    border-radius: 4px;
    background-color: #2d2d2d;
    text-align: center;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #c62828;
    border-radius: 3px;
}
"""


# Light theme stylesheet with white, light grey, and red accents
LIGHT_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #ffffff;
    color: #212121;
}

QLabel {
    color: #212121;
    font-size: 12px;
}

QPushButton {
    background-color: #f5f5f5;
    color: #212121;
    border: 1px solid #cccccc;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #eeeeee;
    border: 1px solid #c62828;
}

QPushButton:pressed {
    background-color: #c62828;
    color: #ffffff;
}

QPushButton#primaryButton {
    background-color: #c62828;
    color: #ffffff;
    border: 1px solid #b71c1c;
}

QPushButton#primaryButton:hover {
    background-color: #d32f2f;
}

QPushButton#primaryButton:pressed {
    background-color: #b71c1c;
}

QPushButton:disabled {
    background-color: #fafafa;
    color: #bdbdbd;
    border: 1px solid #e0e0e0;
}

QLineEdit, QTextEdit {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #cccccc;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #c62828;
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: #fafafa;
    color: #bdbdbd;
}

QListWidget {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #cccccc;
    border-radius: 4px;
    font-size: 12px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #e0e0e0;
}

QListWidget::item:selected {
    background-color: #c62828;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #f5f5f5;
}

QGroupBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    color: #212121;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
}

QCheckBox {
    color: #212121;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #cccccc;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #c62828;
    border: 1px solid #b71c1c;
}

QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #212121;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f5f5f5;
    color: #212121;
    border: 1px solid #cccccc;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #c62828;
    color: #ffffff;
    border-bottom-color: #c62828;
}

QTabBar::tab:hover {
    background-color: #eeeeee;
}

QComboBox {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #cccccc;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
}

QComboBox:hover {
    border: 1px solid #c62828;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #212121;
    selection-background-color: #c62828;
    selection-color: #ffffff;
    border: 1px solid #cccccc;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #e0e0e0;
    border: 1px solid #cccccc;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #c62828;
    border: 1px solid #b71c1c;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #d32f2f;
}

QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #cccccc;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #c62828;
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #e0e0e0;
    text-align: center;
    color: #212121;
}

QProgressBar::chunk {
    background-color: #c62828;
    border-radius: 3px;
}
"""


def get_stylesheet(theme: ThemeName = "dark") -> str:
    """
    Get the stylesheet for the specified theme.

    Args:
        theme: Theme name ("dark" or "light")

    Returns:
        QSS stylesheet string

    Example:
        >>> stylesheet = get_stylesheet("dark")
        >>> app.setStyleSheet(stylesheet)
    """
    if theme == "light":
        return LIGHT_STYLESHEET
    else:
        return DARK_STYLESHEET


def get_available_themes() -> list[str]:
    """
    Get list of available theme names.

    Returns:
        List of theme names

    Example:
        >>> themes = get_available_themes()
        >>> print(f"Available themes: {', '.join(themes)}")
    """
    return ["dark", "light"]
