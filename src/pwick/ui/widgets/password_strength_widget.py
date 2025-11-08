"""
Password strength widget for pwick.

Provides a reusable widget that displays password strength using the zxcvbn algorithm.
Shows a color-coded progress bar and text feedback.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import Qt, Signal

try:
    import zxcvbn

    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False


class PasswordStrengthWidget(QWidget):
    """
    Widget that displays password strength with visual feedback.

    Uses zxcvbn library for accurate password strength estimation.
    Displays a colored progress bar and text label indicating strength level.

    Signals:
        strength_changed(int): Emitted when strength score changes (0-4)
    """

    strength_changed = Signal(int)

    # Strength levels and their colors
    STRENGTH_LEVELS = {
        0: ("Very Weak", "#d32f2f"),  # Red
        1: ("Weak", "#f57c00"),  # Orange
        2: ("Fair", "#fbc02d"),  # Yellow
        3: ("Good", "#7cb342"),  # Light green
        4: ("Strong", "#388e3c"),  # Dark green
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_score = 0
        self._setup_ui()

    def _setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Progress bar for visual strength indication
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(4)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        layout.addWidget(self.progress_bar)

        # Text label for strength description
        self.strength_label = QLabel("Enter password")
        self.strength_label.setAlignment(Qt.AlignCenter)
        self.strength_label.setStyleSheet("font-size: 10px;")
        layout.addWidget(self.strength_label)

        self.setLayout(layout)

        # Set initial color
        self._update_color(0)

    def calculate_strength(self, password: str) -> int:
        """
        Calculate password strength using zxcvbn.

        Args:
            password: Password to evaluate

        Returns:
            Strength score (0-4)
                0 = Very weak (guessed in < 10^3 guesses)
                1 = Weak (guessed in < 10^6 guesses)
                2 = Fair (guessed in < 10^8 guesses)
                3 = Good (guessed in < 10^10 guesses)
                4 = Strong (guessed in >= 10^10 guesses)
        """
        if not ZXCVBN_AVAILABLE:
            # Fallback: Simple length-based estimation
            if not password:
                return 0
            elif len(password) < 8:
                return 0
            elif len(password) < 12:
                return 1
            elif len(password) < 16:
                return 2
            elif len(password) < 20:
                return 3
            else:
                return 4

        if not password:
            return 0

        result = zxcvbn.zxcvbn(password)
        return result["score"]

    def update_password(self, password: str):
        """
        Update the widget to show strength for given password.

        Args:
            password: Password to evaluate and display strength for
        """
        if not password:
            self.progress_bar.setValue(0)
            self.strength_label.setText("Enter password")
            self._update_color(0)
            if self._current_score != 0:
                self._current_score = 0
                self.strength_changed.emit(0)
            return

        score = self.calculate_strength(password)

        self.progress_bar.setValue(score)
        strength_text, _ = self.STRENGTH_LEVELS[score]
        self.strength_label.setText(f"Strength: {strength_text}")
        self._update_color(score)

        if self._current_score != score:
            self._current_score = score
            self.strength_changed.emit(score)

    def _update_color(self, score: int):
        """
        Update the progress bar color based on strength score.

        Args:
            score: Strength score (0-4)
        """
        _, color = self.STRENGTH_LEVELS[score]

        # Update progress bar color using stylesheet
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #404040;
                border-radius: 3px;
                background-color: #2d2d2d;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """
        )

        # Update label color
        self.strength_label.setStyleSheet(
            f"color: {color}; font-size: 10px; font-weight: bold;"
        )

    def get_current_score(self) -> int:
        """
        Get the current strength score.

        Returns:
            Current strength score (0-4)
        """
        return self._current_score

    def is_strong_enough(self, minimum_score: int = 3) -> bool:
        """
        Check if current password meets minimum strength requirement.

        Args:
            minimum_score: Minimum required score (default: 3 = "Good")

        Returns:
            True if password is strong enough, False otherwise
        """
        return self._current_score >= minimum_score
