"""Tab for detecting and removing watermark-like text from PDFs."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from easy_pdf.domain.models import WatermarkCandidate, WatermarkKind
from easy_pdf.gui.tabs.base_tab import BaseTab
from easy_pdf.gui.path_utils import next_available_path
from easy_pdf.gui.widgets import FileSelector, OutputSelector
from easy_pdf.gui.worker import PDFWorker
from easy_pdf.services.bootstrap import Services, bootstrap


@dataclass
class DetectionGroup:
    key: str
    preview_text: str
    occurrence_count: int
    page_count: int
    removable: bool


@dataclass
class DetectWatermarkResult:
    candidates: list[WatermarkCandidate]


@dataclass
class RemoveWatermarkResult:
    output_file: Path
    detected_count: int
    selected_count: int
    changed_pages: int


@dataclass
class DetectionRowState:
    key: str | None
    removable: bool
    checkbox: QCheckBox | None = None


class RemoveWatermarkTab(BaseTab):
    """Tab for removing text watermarks from a PDF file."""

    def __init__(self):
        super().__init__()
        self.services: Optional[Services] = None
        self.worker: Optional[PDFWorker] = None
        self._detected_groups: dict[str, DetectionGroup] = {}
        self._row_states: list[DetectionRowState] = []
        self._init_ui()
        self._clear_detected_groups()
        self._init_services()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        intro = QLabel("先检测疑似水印文字，再勾选确认需要移除的内容，结果输出到新文件。")
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
        self.sensitivity_spin.valueChanged.connect(self._clear_detected_groups)
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

        result_group = QGroupBox("疑似水印文字")
        result_layout = QVBoxLayout()
        self.result_scroll = QScrollArea()
        self.result_scroll.setObjectName("DetectionScrollArea")
        self.result_scroll.setWidgetResizable(True)
        self.result_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.result_scroll.setMinimumHeight(180)
        self.result_scroll.setMaximumHeight(180)

        self.result_content = QWidget()
        self.result_content.setObjectName("DetectionScrollContent")
        self.result_content_layout = QVBoxLayout()
        self.result_content_layout.setContentsMargins(0, 0, 0, 0)
        self.result_content_layout.setSpacing(6)
        self.result_content_layout.addStretch()
        self.result_content.setLayout(self.result_content_layout)
        self.result_scroll.setWidget(self.result_content)
        result_layout.addWidget(self.result_scroll)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("SecondaryBtn")
        self.reset_btn.clicked.connect(self._on_reset)
        self.detect_btn = QPushButton("Detect")
        self.detect_btn.clicked.connect(self._on_detect)
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self._on_remove)
        self.remove_btn.setEnabled(False)
        action_layout.addWidget(self.reset_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.detect_btn)
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
        self._clear_detected_groups()
        self.emit_status("Remove watermark form reset")

    @pyqtSlot(Path)
    def _on_input_file_selected(self, path: Path) -> None:
        self._clear_detected_groups()
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
    def _on_detect(self) -> None:
        if not self.services:
            self.emit_error("Services not initialized")
            return

        input_path = self.file_selector.get_path()
        sensitivity = self.sensitivity_spin.value()

        if not input_path or not input_path.exists():
            self.emit_error("Please select a valid PDF file")
            return

        self.detect_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self._clear_detected_groups()
        self.emit_progress(0)
        self.emit_status("Detecting watermark candidates...")

        self.worker = PDFWorker(self._detect_task, input_path, sensitivity)
        self.worker.signals.started.connect(self._on_worker_started)
        self.worker.signals.finished.connect(self._on_worker_finished)
        self.worker.signals.error.connect(self._on_worker_error)
        self.worker.signals.result.connect(self._on_detect_result)
        self.worker.start()

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

        selected_keys = self._selected_group_keys()
        if not selected_keys:
            self.emit_error("Please select at least one suspected watermark text")
            return

        self.detect_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.emit_progress(0)
        self.emit_status("Removing selected watermark candidates...")

        self.worker = PDFWorker(self._remove_task, input_path, output_path, sensitivity, selected_keys)
        self.worker.signals.started.connect(self._on_worker_started)
        self.worker.signals.finished.connect(self._on_worker_finished)
        self.worker.signals.error.connect(self._on_worker_error)
        self.worker.signals.result.connect(self._on_remove_result)
        self.worker.start()

    def _detect_task(
        self,
        input_path: Path,
        sensitivity: int,
    ) -> DetectWatermarkResult:
        if not self.services:
            raise RuntimeError("Services not initialized")

        self.emit_progress(10)
        src_doc = self.services.document_service.open_document(str(input_path))
        candidates = self.services.watermark_service.detect_watermarks(
            document_id=src_doc.document_id,
            sensitivity=sensitivity,
        )
        self.emit_progress(90)
        return DetectWatermarkResult(candidates=candidates)

    def _remove_task(
        self,
        input_path: Path,
        output_path: Path,
        sensitivity: int,
        selected_keys: list[str],
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
                selected_count=0,
                changed_pages=0,
            )

        selected_candidate_ids = self._resolve_selected_candidate_ids(candidates, selected_keys)
        if not selected_candidate_ids:
            return RemoveWatermarkResult(
                output_file=cleaned_file,
                detected_count=len(candidates),
                selected_count=0,
                changed_pages=0,
            )

        remove_result = self.services.watermark_service.remove_watermarks(
            document_id=working_doc.document_id,
            candidate_ids=selected_candidate_ids,
            structural_delete=True,
            region_inpaint=True,
        )

        self.emit_progress(95)
        return RemoveWatermarkResult(
            output_file=cleaned_file,
            detected_count=len(candidates),
            selected_count=len(selected_candidate_ids),
            changed_pages=remove_result.changed_pages,
        )

    @pyqtSlot()
    def _on_worker_started(self) -> None:
        self.emit_progress(5)

    @pyqtSlot()
    def _on_worker_finished(self) -> None:
        self.detect_btn.setEnabled(True)
        self.remove_btn.setEnabled(bool(self._detected_groups))
        self.emit_progress(100)

    @pyqtSlot(str)
    def _on_worker_error(self, error: str) -> None:
        self.detect_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.emit_error(error)
        self.emit_progress(0)

    @pyqtSlot(object)
    def _on_detect_result(self, result: DetectWatermarkResult) -> None:
        self._populate_detected_groups(result.candidates)
        detected_count = len(result.candidates)
        if detected_count == 0:
            self.emit_status("No watermark-like text detected")
            return

        self.emit_status("Detected suspected content. Only explicitly check safe removable items.")

    @pyqtSlot(object)
    def _on_remove_result(self, result: RemoveWatermarkResult) -> None:
        self._row_states = []
        self._add_info_row(f"Output: {result.output_file}")
        self._add_info_row(f"Detected candidates: {result.detected_count}")
        self._add_info_row(f"Selected candidates: {result.selected_count}")
        self._add_info_row(f"Changed pages: {result.changed_pages}")

        if result.detected_count == 0:
            self.emit_status(f"No watermark-like text detected. Output copied to: {result.output_file}")
        elif result.selected_count == 0:
            self.emit_status("No selected candidates matched the output copy. Try running detection again.")
        else:
            self.emit_status(
                f"Watermark removal complete: {result.changed_pages} pages changed. Output: {result.output_file}"
            )

    def _populate_detected_groups(self, candidates: list[WatermarkCandidate]) -> None:
        self._detected_groups = {}
        self._row_states = []
        self._clear_result_rows()

        grouped: dict[str, dict[str, object]] = {}
        for candidate in candidates:
            key = self._candidate_group_key(candidate)
            group = grouped.setdefault(
                key,
                {
                    "preview_text": candidate.preview_text.strip(),
                    "occurrence_count": 0,
                    "pages": set(),
                    "removable": candidate.removable,
                    "kind": candidate.kind,
                },
            )
            group["occurrence_count"] = int(group["occurrence_count"]) + 1
            group["pages"].add(candidate.page_index)
            group["removable"] = bool(group["removable"]) and candidate.removable

        if not grouped:
            self._add_info_row("No suspected watermark text found in this build.")
            self.remove_btn.setEnabled(False)
            return

        sorted_groups = sorted(
            grouped.items(),
            key=lambda item: (-len(item[1]["pages"]), -int(item[1]["occurrence_count"]), str(item[1]["preview_text"])),
        )

        for key, data in sorted_groups:
            group = DetectionGroup(
                key=key,
                preview_text=str(data["preview_text"]),
                occurrence_count=int(data["occurrence_count"]),
                page_count=len(data["pages"]),
                removable=bool(data["removable"]),
            )
            self._detected_groups[key] = group
            label = self._group_label(group)
            self._add_group_row(group, label)

        self.remove_btn.setEnabled(any(group.removable for group in self._detected_groups.values()))

    def _selected_group_keys(self) -> list[str]:
        selected: list[str] = []
        for row_state in self._row_states:
            if row_state.key and row_state.checkbox and row_state.checkbox.isChecked():
                selected.append(row_state.key)
        return selected

    def _clear_detected_groups(self, *_args: object) -> None:
        self._detected_groups = {}
        self._row_states = []
        self._clear_result_rows()
        self._add_info_row("Click Detect to list suspected watermark text.")
        self.remove_btn.setEnabled(False)

    @staticmethod
    def _candidate_group_key(candidate: WatermarkCandidate) -> str:
        kind = candidate.kind.value
        text = " ".join(candidate.preview_text.split()) or kind
        return f"{kind}::{text.lower()}"

    @classmethod
    def _resolve_selected_candidate_ids(
        cls,
        candidates: list[WatermarkCandidate],
        selected_keys: list[str],
    ) -> list[str]:
        selected_key_set = set(selected_keys)
        selected_ids: set[str] = set()

        for candidate in candidates:
            key = cls._candidate_group_key(candidate)
            if key in selected_key_set and candidate.removable:
                selected_ids.add(candidate.candidate_id)

        return sorted(selected_ids)

    @staticmethod
    def _group_label(group: DetectionGroup) -> str:
        preview = group.preview_text.replace("\n", " ")
        if len(preview) > 80:
            preview = f"{preview[:77]}..."
        if group.removable:
            suffix = "safe to remove"
        else:
            suffix = "preview only; may overlap real content"
        return f"{preview}  |  {group.page_count} pages / {group.occurrence_count} hits  |  {suffix}"

    def _add_group_row(self, group: DetectionGroup, label: str) -> None:
        container = QWidget()
        container.setObjectName("DetectionRow")
        container.setMinimumHeight(60)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        checkbox: QCheckBox | None = None
        if group.removable:
            checkbox = QCheckBox()
            checkbox.setObjectName("DetectionRowCheckbox")
            checkbox.setChecked(False)
            layout.addWidget(checkbox, 0, Qt.AlignmentFlag.AlignTop)
        else:
            badge = QLabel("Preview")
            badge.setObjectName("DetectionPreviewBadge")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setMinimumWidth(58)
            layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)

        label_widget = QLabel(label)
        label_widget.setObjectName("DetectionRowLabel")
        label_widget.setWordWrap(True)
        label_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(label_widget, 1)

        container.setLayout(layout)
        self._insert_result_row(container)
        self._row_states.append(DetectionRowState(key=group.key, removable=group.removable, checkbox=checkbox))

    def _add_info_row(self, text: str) -> None:
        container = QWidget()
        container.setObjectName("DetectionInfoRow")
        container.setMinimumHeight(44)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(0)
        label_widget = QLabel(text)
        label_widget.setObjectName("DetectionInfoLabel")
        label_widget.setWordWrap(True)
        label_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label_widget)
        container.setLayout(layout)
        self._insert_result_row(container)
        self._row_states.append(DetectionRowState(key=None, removable=False, checkbox=None))

    def _clear_result_rows(self) -> None:
        while self.result_content_layout.count() > 1:
            item = self.result_content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _insert_result_row(self, widget: QWidget) -> None:
        insert_index = max(0, self.result_content_layout.count() - 1)
        self.result_content_layout.insertWidget(insert_index, widget)
