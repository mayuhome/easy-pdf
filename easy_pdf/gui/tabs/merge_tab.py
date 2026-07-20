"""Merge tab for merging PDF files."""
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

from easy_pdf.gui.tabs.base_tab import BaseTab
from easy_pdf.gui.widgets import OutputSelector
from easy_pdf.gui.worker import PDFWorker
from easy_pdf.services.bootstrap import Services, bootstrap


class MergeTab(BaseTab):
    """Tab for merging multiple PDF files."""

    def __init__(self):
        super().__init__()
        self.services: Optional[Services] = None
        self.worker: Optional[PDFWorker] = None
        self.pdf_files: list[Path] = []
        self._init_ui()
        self._init_services()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        intro = QLabel("按顺序合并多个 PDF，拖动上下顺序可控制最终页序。")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # File list
        list_group = QGroupBox("Step 1 · 选择并排序文件")
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)
        self.file_list = QListWidget()
        list_layout.addWidget(self.file_list)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        self.add_btn = QPushButton("Add PDFs")
        self.add_btn.setObjectName("SecondaryBtn")
        self.add_btn.clicked.connect(self._on_add_files)
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.setObjectName("SecondaryBtn")
        self.remove_btn.clicked.connect(self._on_remove_file)
        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.setObjectName("SecondaryBtn")
        self.move_up_btn.clicked.connect(self._on_move_up)
        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.setObjectName("SecondaryBtn")
        self.move_down_btn.clicked.connect(self._on_move_down)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.move_up_btn)
        button_layout.addWidget(self.move_down_btn)
        list_layout.addLayout(button_layout)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Output directory
        output_group = QGroupBox("Step 2 · 选择输出目录")
        output_layout = QVBoxLayout()
        self.output_selector = OutputSelector("Output Directory")
        output_layout.addWidget(self.output_selector)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Merge button
        merge_layout = QHBoxLayout()
        merge_layout.setSpacing(8)
        self.clear_btn = QPushButton("Clear List")
        self.clear_btn.setObjectName("SecondaryBtn")
        self.clear_btn.clicked.connect(self._on_clear_list)
        self.merge_btn = QPushButton("Merge PDFs")
        self.merge_btn.clicked.connect(self._on_merge)
        merge_layout.addWidget(self.clear_btn)
        merge_layout.addStretch()
        merge_layout.addWidget(self.merge_btn)
        layout.addLayout(merge_layout)

        layout.addStretch()
        self.setLayout(layout)

    @pyqtSlot()
    def _on_clear_list(self) -> None:
        """Clear selected files."""
        self.pdf_files.clear()
        self.file_list.clear()
        self.emit_status("Merge file list cleared")

    def _init_services(self) -> None:
        """Initialize services."""
        try:
            self.services = bootstrap()
            self.emit_status("Merge service ready")
        except Exception as e:
            self.emit_error(f"Failed to initialize services: {str(e)}")

    @pyqtSlot()
    def _on_add_files(self) -> None:
        """Handle add files button click."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf);;All Files (*)"
        )
        for file in files:
            path = Path(file)
            if path not in self.pdf_files:
                self.pdf_files.append(path)
                self.file_list.addItem(path.name)

    @pyqtSlot()
    def _on_remove_file(self) -> None:
        """Handle remove file button click."""
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            self.pdf_files.pop(current_row)
            self.file_list.takeItem(current_row)

    @pyqtSlot()
    def _on_move_up(self) -> None:
        """Move selected file up in the list."""
        current_row = self.file_list.currentRow()
        if current_row > 0:
            self.pdf_files[current_row], self.pdf_files[current_row - 1] = (
                self.pdf_files[current_row - 1],
                self.pdf_files[current_row],
            )
            self._refresh_list(current_row - 1)

    @pyqtSlot()
    def _on_move_down(self) -> None:
        """Move selected file down in the list."""
        current_row = self.file_list.currentRow()
        if current_row >= 0 and current_row < len(self.pdf_files) - 1:
            self.pdf_files[current_row], self.pdf_files[current_row + 1] = (
                self.pdf_files[current_row + 1],
                self.pdf_files[current_row],
            )
            self._refresh_list(current_row + 1)

    def _refresh_list(self, select_index: int = 0) -> None:
        """Refresh the file list display."""
        self.file_list.clear()
        for path in self.pdf_files:
            self.file_list.addItem(path.name)
        if select_index < len(self.pdf_files):
            self.file_list.setCurrentRow(select_index)

    @pyqtSlot()
    def _on_merge(self) -> None:
        """Handle merge button click."""
        if not self.services:
            self.emit_error("Services not initialized")
            return

        if not self.pdf_files:
            self.emit_error("Please add at least one PDF file")
            return

        output_path = self.output_selector.get_path()
        if not output_path:
            self.emit_error("Please select an output directory")
            return

        self.merge_btn.setEnabled(False)
        self.emit_progress(0)
        self.emit_status("Merging PDFs...")

        self.worker = PDFWorker(self._merge_task, self.pdf_files, output_path)
        self.worker.signals.started.connect(self._on_worker_started)
        self.worker.signals.finished.connect(self._on_worker_finished)
        self.worker.signals.error.connect(self._on_worker_error)
        self.worker.signals.result.connect(self._on_worker_result)
        self.worker.start()

    def _merge_task(self, pdf_files: list[Path], output_path: Path) -> Path:
        """Task to merge PDFs."""
        if not self.services:
            raise RuntimeError("Services not initialized")

        output_file = output_path / "merged.pdf"
        self.services.page_edit_service.merge_documents(pdf_files, output_file)
        return output_file

    @pyqtSlot()
    def _on_worker_started(self) -> None:
        """Handle worker started."""
        self.emit_progress(50)

    @pyqtSlot()
    def _on_worker_finished(self) -> None:
        """Handle worker finished."""
        self.merge_btn.setEnabled(True)
        self.emit_progress(100)

    @pyqtSlot(str)
    def _on_worker_error(self, error: str) -> None:
        """Handle worker error."""
        self.merge_btn.setEnabled(True)
        self.emit_error(error)
        self.emit_progress(0)

    @pyqtSlot(object)
    def _on_worker_result(self, result: Path) -> None:
        """Handle worker result."""
        self.emit_status(f"PDFs merged successfully: {result}")
