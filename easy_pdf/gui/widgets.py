"""Reusable UI widgets for the PDF application."""
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class FileSelector(QWidget):
    """Widget for selecting a file with a browse button."""

    file_selected = pyqtSignal(Path)

    def __init__(self, label: str = "Select File", file_filter: str = "All Files (*)"):
        super().__init__()
        self.file_filter = file_filter
        self._init_ui(label)

    def _init_ui(self, label: str) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label_widget = QLabel(label)
        label_widget.setObjectName("StepTitle")
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("No file selected")
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setObjectName("SecondaryBtn")
        self.browse_btn.clicked.connect(self._browse)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(self.path_input, 1)
        row.addWidget(self.browse_btn, 0)

        layout.addWidget(label_widget)
        layout.addLayout(row)

        self.setLayout(layout)

    def _browse(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", self.file_filter
        )
        if file_path:
            path = Path(file_path)
            self.path_input.setText(str(path))
            self.file_selected.emit(path)

    def get_path(self) -> Optional[Path]:
        """Get the selected file path."""
        text = self.path_input.text()
        return Path(text) if text else None

    def set_path(self, path: Path) -> None:
        """Set the file path."""
        self.path_input.setText(str(path))


class OutputSelector(QWidget):
    """Widget for selecting output directory."""

    path_selected = pyqtSignal(Path)

    def __init__(self, label: str = "Output Directory"):
        super().__init__()
        self._init_ui(label)

    def _init_ui(self, label: str) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label_widget = QLabel(label)
        label_widget.setObjectName("StepTitle")
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("No directory selected")
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setObjectName("SecondaryBtn")
        self.browse_btn.clicked.connect(self._browse)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(self.path_input, 1)
        row.addWidget(self.browse_btn, 0)

        layout.addWidget(label_widget)
        layout.addLayout(row)

        self.setLayout(layout)

    def _browse(self) -> None:
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            path = Path(dir_path)
            self.path_input.setText(str(path))
            self.path_selected.emit(path)

    def get_path(self) -> Optional[Path]:
        """Get the selected directory path."""
        text = self.path_input.text()
        return Path(text) if text else None

    def set_path(self, path: Path) -> None:
        """Set the directory path."""
        self.path_input.setText(str(path))


class WatermarkPanel(QGroupBox):
    """Panel for watermark configuration."""

    def __init__(self):
        super().__init__("Watermark Settings")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Text input
        text_layout = QHBoxLayout()
        text_layout.setSpacing(8)
        text_layout.addWidget(QLabel("Text:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter watermark text")
        text_layout.addWidget(self.text_input)
        layout.addLayout(text_layout)

        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setMinimum(10)
        self.opacity_spin.setMaximum(100)
        self.opacity_spin.setValue(28)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.setMinimumWidth(120)
        opacity_layout.addWidget(self.opacity_spin)
        opacity_layout.addStretch()
        layout.addLayout(opacity_layout)

        # Font size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setMinimum(8)
        self.size_spin.setMaximum(120)
        self.size_spin.setValue(48)
        self.size_spin.setMinimumWidth(120)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        layout.addLayout(size_layout)

        self.setLayout(layout)

    def get_watermark_config(self) -> dict:
        """Get watermark configuration."""
        return {
            "text": self.text_input.text(),
            "opacity": self.opacity_spin.value() / 100.0,
            "font_size": self.size_spin.value(),
        }

    def set_watermark_config(self, text: str, opacity: float = 0.28, font_size: int = 48) -> None:
        """Set watermark configuration."""
        self.text_input.setText(text)
        self.opacity_spin.setValue(int(opacity * 100))
        self.size_spin.setValue(font_size)
