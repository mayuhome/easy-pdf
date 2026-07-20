"""Tab for detecting and removing watermark-like text from PDFs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from easy_pdf.gui.tabs.base_tab import BaseTab
from easy_pdf.gui.path_utils import next_available_path
from easy_pdf.gui.widgets import FileSelector, OutputSelector
from easy_pdf.gui.worker import PDFWorker
from easy_pdf.services.bootstrap import Services, bootstrap


@dataclass
class RemoveWatermarkResult:
    output_file: Path
    detected_count: int
    changed_pages: int


class RemoveWatermarkTab(BaseTab):
    """Tab for removing text watermarks from a PDF file."""

    def __init__(self):
        super().__init__()
        self.services: Optional[Services] = None
        self.worker: Optional[PDFWorker] = None
        self._init_ui()
        self._init_services()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        intro = QLabel("检测并移除 PDF 中疑似水印文本，结果输出到新文件。")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        source_group = QGroupBox("Step 1 · 选择 PDF 文件")
        source_layout = QVBoxLayout()
        self.file_selector = FileSelector("PDF File", "PDF Files (*.pdf);;All Files (*)")
        self.file_selector.file_selected.connect(self._on_input_file_selected)
        source_layout.addWidget(self.file_selector)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        config_group = QGroupBox("Step 2 · 检测参数")
        config_layout = QHBoxLayout()
        config_layout.setSpacing(8)
        config_layout.addWidget(QLabel("Sensitivity"))
        self.sensitivity_spin = QSpinBox()
        self.sensitivity_spin.setMinimum(1)
        self.sensitivity_spin.setMaximum(5)
        self.sensitivity_spin.setValue(3)
        self.sensitivity_spin.setMinimumWidth(120)
        config_layout.addWidget(self.sensitivity_spin)
        config_layout.addStretch()
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        output_group = QGroupBox("Step 3 · 选择输出目录")
        output_layout = QVBoxLayout()
        self.save_to_source_cb = QCheckBox("Save to source directory")
        self.save_to_source_cb.toggled.connect(self._on_save_to_source_toggled)
        output_layout.addWidget(self.save_to_source_cb)
        self.output_selector = OutputSelector("Output Directory")
        output_layout.addWidget(self.output_selector)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        result_group = QGroupBox("Detection Preview")
        result_layout = QVBoxLayout()
        self.result_list = QListWidget()
        result_layout.addWidget(self.result_list)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("SecondaryBtn")
        self.reset_btn.clicked.connect(self._on_reset)
        self.remove_btn = QPushButton("Detect & Remove")
        self.remove_btn.clicked.connect(self._on_remove)
        action_layout.addWidget(self.reset_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.remove_btn)
        layout.addLayout(action_layout)

        layout.addStretch()
        self.setLayout(layout)

    def _init_services(self) -> None:
        try:
            self.services = bootstrap()
            self.emit_status("Remove watermark service ready")
        except Exception as e:
            self.emit_error(f"Failed to initialize services: {str(e)}")

    @pyqtSlot()
    def _on_reset(self) -> None:
        self.file_selector.path_input.clear()
        self.output_selector.path_input.clear()
        self.save_to_source_cb.setChecked(False)
        self.output_selector.setEnabled(True)
        self.sensitivity_spin.setValue(3)
        self.result_list.clear()
        self.emit_status("Remove watermark form reset")

    @pyqtSlot(Path)
    def _on_input_file_selected(self, path: Path) -> None:
        if self.save_to_source_cb.isChecked():
            self.output_selector.set_path(path.parent)

    @pyqtSlot(bool)
    def _on_save_to_source_toggled(self, checked: bool) -> None:
        self.output_selector.setEnabled(not checked)
        if checked:
            input_path = self.file_selector.get_path()
            if input_path:
                self.output_selector.set_path(input_path.parent)

    @pyqtSlot()
    def _on_remove(self) -> None:
        if not self.services:
            self.emit_error("Services not initialized")
            return

        input_path = self.file_selector.get_path()
        output_path = self.output_selector.get_path()
        sensitivity = self.sensitivity_spin.value()

        if not input_path or not input_path.exists():
            self.emit_error("Please select a valid PDF file")
            return

        if not output_path:
            self.emit_error("Please select an output directory")
            return

        if self.save_to_source_cb.isChecked() and input_path:
            output_path = input_path.parent

        self.remove_btn.setEnabled(False)
        self.result_list.clear()
        self.emit_progress(0)
        self.emit_status("Detecting and removing watermarks...")

        self.worker = PDFWorker(self._remove_task, input_path, output_path, sensitivity)
        self.worker.signals.started.connect(self._on_worker_started)
        self.worker.signals.finished.connect(self._on_worker_finished)
        self.worker.signals.error.connect(self._on_worker_error)
        self.worker.signals.result.connect(self._on_worker_result)
        self.worker.start()

    def _remove_task(
        self,
        input_path: Path,
        output_path: Path,
        sensitivity: int,
    ) -> RemoveWatermarkResult:
        if not self.services:
            raise RuntimeError("Services not initialized")

        self.emit_progress(10)

        src_doc = self.services.document_service.open_document(str(input_path))
        cleaned_file = next_available_path(output_path / f"{input_path.stem}_cleaned.pdf")
        self.services.document_service.save_document(
            document_id=src_doc.document_id,
            output_path=str(cleaned_file),
            backup=False,
        )

        self.emit_progress(35)

        working_doc = self.services.document_service.open_document(str(cleaned_file))
        candidates = self.services.watermark_service.detect_watermarks(
            document_id=working_doc.document_id,
            sensitivity=sensitivity,
        )

        self.emit_progress(70)

        if not candidates:
            return RemoveWatermarkResult(
                output_file=cleaned_file,
                detected_count=0,
                changed_pages=0,
            )

        remove_result = self.services.watermark_service.remove_watermarks(
            document_id=working_doc.document_id,
            candidate_ids=[candidate.candidate_id for candidate in candidates],
            structural_delete=True,
            region_inpaint=True,
        )

        self.emit_progress(95)
        return RemoveWatermarkResult(
            output_file=cleaned_file,
            detected_count=len(candidates),
            changed_pages=remove_result.changed_pages,
        )

    @pyqtSlot()
    def _on_worker_started(self) -> None:
        self.emit_progress(5)

    @pyqtSlot()
    def _on_worker_finished(self) -> None:
        self.remove_btn.setEnabled(True)
        self.emit_progress(100)

    @pyqtSlot(str)
    def _on_worker_error(self, error: str) -> None:
        self.remove_btn.setEnabled(True)
        self.emit_error(error)
        self.emit_progress(0)

    @pyqtSlot(object)
    def _on_worker_result(self, result: RemoveWatermarkResult) -> None:
        self.result_list.clear()
        self.result_list.addItem(f"Output: {result.output_file}")
        self.result_list.addItem(f"Detected candidates: {result.detected_count}")
        self.result_list.addItem(f"Changed pages: {result.changed_pages}")

        if result.detected_count == 0:
            self.emit_status(f"No watermark-like text detected. Output copied to: {result.output_file}")
        else:
            self.emit_status(
                f"Watermark removal complete: {result.changed_pages} pages changed. Output: {result.output_file}"
            )
