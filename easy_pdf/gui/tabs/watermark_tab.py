"""Watermark tab for adding watermarks to PDFs."""
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from easy_pdf.gui.tabs.base_tab import BaseTab
from easy_pdf.gui.widgets import FileSelector, OutputSelector, WatermarkPanel
from easy_pdf.gui.worker import PDFWorker
from easy_pdf.services.bootstrap import Services, bootstrap


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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        intro = QLabel("为单个 PDF 添加文字水印，保持原文件不变并输出新文件。")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # File selector
        source_group = QGroupBox("Step 1 · 选择 PDF 文件")
        source_layout = QVBoxLayout()
        self.file_selector = FileSelector("PDF File", "PDF Files (*.pdf);;All Files (*)")
        source_layout.addWidget(self.file_selector)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        # Watermark settings
        watermark_group = QGroupBox("Step 2 · 设置水印")
        watermark_layout = QVBoxLayout()
        self.watermark_panel = WatermarkPanel()
        watermark_layout.addWidget(self.watermark_panel)
        watermark_group.setLayout(watermark_layout)
        layout.addWidget(watermark_group)

        # Output directory
        output_group = QGroupBox("Step 3 · 选择输出目录")
        output_layout = QVBoxLayout()
        self.output_selector = OutputSelector("Output Directory")
        output_layout.addWidget(self.output_selector)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("SecondaryBtn")
        self.reset_btn.clicked.connect(self._on_reset)
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setObjectName("SecondaryBtn")
        self.preview_btn.clicked.connect(self._on_preview)
        self.apply_btn = QPushButton("Apply Watermark")
        self.apply_btn.clicked.connect(self._on_apply)
        button_layout.setSpacing(8)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.preview_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

    @pyqtSlot()
    def _on_reset(self) -> None:
        """Reset form inputs."""
        self.file_selector.path_input.clear()
        self.output_selector.path_input.clear()
        self.watermark_panel.set_watermark_config("", 0.28, 48)
        self.emit_status("Watermark form reset")

    @pyqtSlot()
    def _on_preview(self) -> None:
        """Preview watermark style with current settings."""
        config = self.watermark_panel.get_watermark_config()
        text = config["text"].strip()
        if not text:
            self.emit_error("Please enter watermark text before preview")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Watermark Preview")
        dialog.setMinimumSize(620, 780)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        info = QLabel("Preview style: diagonal, light gray, large-size watermark")
        info.setWordWrap(True)
        layout.addWidget(info)

        preview_label = QLabel()
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setPixmap(
            self._build_preview_pixmap(
                text=text,
                opacity=config["opacity"],
                font_size=config["font_size"],
            )
        )
        layout.addWidget(preview_label)

        dialog.setLayout(layout)
        dialog.exec()

    def _build_preview_pixmap(self, text: str, opacity: float, font_size: int) -> QPixmap:
        """Render a simple visual preview using current watermark settings."""
        width = 560
        height = 740
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#f8fafc"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Page-like canvas area
        page_x = 30
        page_y = 20
        page_w = width - 60
        page_h = height - 40
        painter.setPen(QPen(QColor("#d1d5db"), 1))
        painter.setBrush(QColor("#ffffff"))
        painter.drawRect(page_x, page_y, page_w, page_h)

        clamped_opacity = min(0.6, max(0.12, float(opacity)))
        adaptive_font = max(28, int(font_size))
        adaptive_font = min(adaptive_font, 120)

        painter.save()
        center_x = page_x + page_w // 2
        center_y = page_y + page_h // 2
        painter.translate(center_x, center_y)
        painter.rotate(-35)
        painter.shear(-0.28, 0)

        font = QFont("Times New Roman", adaptive_font)
        font.setItalic(True)
        painter.setFont(font)

        color = QColor("#b8b8b8")
        color.setAlphaF(clamped_opacity)
        painter.setPen(color)

        text_rect_w = int(page_w * 1.25)
        text_rect_h = int(page_h * 0.35)
        painter.drawText(
            -text_rect_w // 2,
            -text_rect_h // 2,
            text_rect_w,
            text_rect_h,
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            text,
        )
        painter.restore()

        painter.end()
        return pixmap

    def _init_services(self) -> None:
        """Initialize services."""
        try:
            self.services = bootstrap()
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
            opacity=config["opacity"],
            font_size=config["font_size"],
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
