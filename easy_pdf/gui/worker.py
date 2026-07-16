"""Background worker threads for GUI operations."""
from pathlib import Path
from typing import Any, Callable, Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from easy_pdf.domain.errors import PDFOperationError


class WorkerSignals(QObject):
    """Signals emitted by worker threads."""

    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)  # progress %, status message
    result = pyqtSignal(object)


class PDFWorker(QThread):
    """Worker thread for long-running PDF operations."""

    def __init__(self, operation: Callable[..., Any], *args: Any, **kwargs: Any):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:
        """Execute the operation in a separate thread."""
        try:
            self.signals.started.emit()
            result = self.operation(*self.args, **self.kwargs)
            self.signals.result.emit(result)
            self.signals.finished.emit()
        except PDFOperationError as e:
            self.signals.error.emit(f"PDF操作错误: {str(e)}")
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(f"发生错误: {str(e)}")
            self.signals.finished.emit()
