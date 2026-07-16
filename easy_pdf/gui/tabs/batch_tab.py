"""Batch processing tab for processing multiple files."""
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from easy_pdf.gui.tabs.base_tab import BaseTab
from easy_pdf.gui.widgets import OutputSelector, WatermarkPanel
from easy_pdf.gui.worker import PDFWorker
from easy_pdf.services.bootstrap import Services


class BatchProcessTab(BaseTab):
    """Tab for batch processing PDF files."""

    def __init__(self):
        super().__init__()
        self.services: Optional[Services] = None
        self.worker: Optional[PDFWorker] = None
        self.input_directory: Optional[Path] = None
        self._init_ui()
        self._init_services()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Input directory selector
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input Directory:"))
        self.input_path_display = QLineEdit()
        self.input_path_display.setReadOnly(True)
        input_layout.addWidget(self.input_path_display)
        self.input_browse_btn = QPushButton("Browse...")
        self.input_browse_btn.clicked.connect(self._on_browse_input)
        input_layout.addWidget(self.input_browse_btn)
        layout.addLayout(input_layout)

        # Options
        options_layout = QVBoxLayout()
        self.apply_watermark_cb = QCheckBox("Apply Watermark to All PDFs")
        self.apply_watermark_cb.setChecked(True)
        self.apply_watermark_cb.toggled.connect(self._on_watermark_toggled)
        options_layout.addWidget(self.apply_watermark_cb)

        # Watermark settings (conditional)
        self.watermark_panel = WatermarkPanel()
        options_layout.addWidget(self.watermark_panel)

        layout.addLayout(options_layout)

        # Output directory
        self.output_selector = OutputSelector("Output Directory:")
        layout.addWidget(self.output_selector)

        # Process button
        process_layout = QHBoxLayout()
        self.process_btn = QPushButton("Start Batch Processing")
        self.process_btn.clicked.connect(self._on_process)
        process_layout.addStretch()
        process_layout.addWidget(self.process_btn)
        process_layout.addStretch()
        layout.addLayout(process_layout)

        layout.addStretch()
        self.setLayout(layout)

    def _init_services(self) -> None:
        """Initialize services."""
        try:
            self.services = Services.bootstrap()
            self.emit_status("Batch processing service ready")
        except Exception as e:
            self.emit_error(f"Failed to initialize services: {str(e)}")

    @pyqtSlot()
    def _on_browse_input(self) -> None:
        """Handle input directory browse."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_directory = Path(dir_path)
            self.input_path_display.setText(str(self.input_directory))

    @pyqtSlot(bool)
    def _on_watermark_toggled(self, checked: bool) -> None:
        """Handle watermark checkbox toggle."""
        self.watermark_panel.setEnabled(checked)

    @pyqtSlot()
    def _on_process(self) -> None:
        """Handle process button click."""
        if not self.services:
            self.emit_error("Services not initialized")
            return

        if not self.input_directory or not self.input_directory.exists():
            self.emit_error("Please select a valid input directory")
            return

        output_path = self.output_selector.get_path()
        if not output_path:
            self.emit_error("Please select an output directory")
            return

        # Get PDF files
        pdf_files = list(self.input_directory.glob("*.pdf"))
        if not pdf_files:
            self.emit_error("No PDF files found in the input directory")
            return

        self.process_btn.setEnabled(False)
        self.emit_progress(0)
        self.emit_status(f"Processing {len(pdf_files)} files...")

        watermark_config = None
        if self.apply_watermark_cb.isChecked():
            watermark_config = self.watermark_panel.get_watermark_config()
            if not watermark_config["text"]:
                self.emit_error("Please enter watermark text if watermarking is enabled")
                self.process_btn.setEnabled(True)
                return

        self.worker = PDFWorker(
            self._process_batch_task, pdf_files, output_path, watermark_config
        )
        self.worker.signals.started.connect(self._on_worker_started)
        self.worker.signals.finished.connect(self._on_worker_finished)
        self.worker.signals.error.connect(self._on_worker_error)
        self.worker.signals.result.connect(self._on_worker_result)
        self.worker.start()

    def _process_batch_task(
        self, pdf_files: list[Path], output_path: Path, watermark_config: Optional[dict]
    ) -> int:
        """Task to process batch of PDFs."""
        if not self.services:
            raise RuntimeError("Services not initialized")

        processed_count = 0
        total = len(pdf_files)

        for idx, pdf_file in enumerate(pdf_files):
            try:
                if watermark_config:
                    output_file = output_path / f"{pdf_file.stem}_watermarked.pdf"
                    self.services.watermark_service.apply_to_document(
                        input_file=pdf_file,
                        output_file=output_file,
                        text=watermark_config["text"],
                    )
                else:
                    # Just copy the file
                    output_file = output_path / pdf_file.name
                    output_file.write_bytes(pdf_file.read_bytes())

                processed_count += 1
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")

            # Update progress
            progress = int((idx + 1) / total * 100)
            self.emit_progress(progress)

        return processed_count

    @pyqtSlot()
    def _on_worker_started(self) -> None:
        """Handle worker started."""
        self.emit_progress(10)

    @pyqtSlot()
    def _on_worker_finished(self) -> None:
        """Handle worker finished."""
        self.process_btn.setEnabled(True)
        self.emit_progress(100)

    @pyqtSlot(str)
    def _on_worker_error(self, error: str) -> None:
        """Handle worker error."""
        self.process_btn.setEnabled(True)
        self.emit_error(error)
        self.emit_progress(0)

    @pyqtSlot(object)
    def _on_worker_result(self, result: int) -> None:
        """Handle worker result."""
        output_path = self.output_selector.get_path()
        self.emit_status(f"Batch processing completed: {result} files processed. Output: {output_path}")
