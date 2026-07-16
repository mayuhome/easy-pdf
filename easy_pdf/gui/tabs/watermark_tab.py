"""Watermark tab for adding watermarks to PDFs."""
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)

from easy_pdf.gui.tabs.base_tab import BaseTab
from easy_pdf.gui.widgets import FileSelector, OutputSelector, WatermarkPanel
from easy_pdf.gui.worker import PDFWorker
from easy_pdf.services.bootstrap import Services


class WatermarkTab(BaseTab):
    """Tab for adding watermarks to PDF files."""

    def __init__(self):
        super().__init__()
        self.services: Optional[Services] = None
        self.worker: Optional[PDFWorker] = None
        self._init_ui()
        self._init_services()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # File selector
        self.file_selector = FileSelector("PDF File:", "PDF Files (*.pdf);;All Files (*)")
        layout.addWidget(self.file_selector)

        # Watermark settings
        self.watermark_panel = WatermarkPanel()
        layout.addWidget(self.watermark_panel)

        # Output directory
        self.output_selector = OutputSelector("Output Directory:")
        layout.addWidget(self.output_selector)

        # Buttons
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Watermark")
        self.apply_btn.clicked.connect(self._on_apply)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

    def _init_services(self) -> None:
        """Initialize services."""
        try:
            self.services = Services.bootstrap()
            self.emit_status("Watermark service ready")
        except Exception as e:
            self.emit_error(f"Failed to initialize services: {str(e)}")

    @pyqtSlot()
    def _on_apply(self) -> None:
        """Handle apply watermark button click."""
        if not self.services:
            self.emit_error("Services not initialized")
            return

        input_path = self.file_selector.get_path()
        output_path = self.output_selector.get_path()

        if not input_path or not input_path.exists():
            self.emit_error("Please select a valid PDF file")
            return

        if not output_path:
            self.emit_error("Please select an output directory")
            return

        watermark_config = self.watermark_panel.get_watermark_config()

        if not watermark_config["text"]:
            self.emit_error("Please enter watermark text")
            return

        # Create worker thread
        self.apply_btn.setEnabled(False)
        self.emit_progress(0)
        self.emit_status("Applying watermark...")

        self.worker = PDFWorker(
            self._apply_watermark_task,
            input_path,
            output_path,
            watermark_config,
        )
        self.worker.signals.started.connect(self._on_worker_started)
        self.worker.signals.finished.connect(self._on_worker_finished)
        self.worker.signals.error.connect(self._on_worker_error)
        self.worker.signals.result.connect(self._on_worker_result)
        self.worker.start()

    def _apply_watermark_task(
        self, input_path: Path, output_path: Path, config: dict
    ) -> Path:
        """Task to apply watermark."""
        if not self.services:
            raise RuntimeError("Services not initialized")

        output_file = output_path / f"{input_path.stem}_watermarked.pdf"
        self.services.watermark_service.apply_to_document(
            input_file=input_path,
            output_file=output_file,
            text=config["text"],
        )
        return output_file

    @pyqtSlot()
    def _on_worker_started(self) -> None:
        """Handle worker started."""
        self.emit_progress(50)

    @pyqtSlot()
    def _on_worker_finished(self) -> None:
        """Handle worker finished."""
        self.apply_btn.setEnabled(True)
        self.emit_progress(100)

    @pyqtSlot(str)
    def _on_worker_error(self, error: str) -> None:
        """Handle worker error."""
        self.apply_btn.setEnabled(True)
        self.emit_error(error)
        self.emit_progress(0)

    @pyqtSlot(object)
    def _on_worker_result(self, result: Path) -> None:
        """Handle worker result."""
        self.emit_status(f"Watermark applied successfully: {result}")
