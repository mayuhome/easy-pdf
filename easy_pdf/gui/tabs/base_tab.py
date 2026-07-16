"""Base tab class for PDF operations."""
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget


class BaseTab(QWidget):
    """Base class for operation tabs."""

    status_changed = pyqtSignal(str)
    progress_changed = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def emit_status(self, message: str) -> None:
        """Emit status message."""
        self.status_changed.emit(message)

    def emit_progress(self, progress: int) -> None:
        """Emit progress update (0-100)."""
        self.progress_changed.emit(progress)

    def emit_error(self, error: str) -> None:
        """Emit error message."""
        self.error_occurred.emit(error)
