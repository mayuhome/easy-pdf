"""Main window for the PDF toolkit GUI application."""
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from easy_pdf.gui.tabs.batch_tab import BatchProcessTab
from easy_pdf.gui.tabs.merge_tab import MergeTab
from easy_pdf.gui.tabs.watermark_tab import WatermarkTab


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy PDF - PDF Toolkit")
        self.setGeometry(100, 100, 1000, 700)
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Tab widget
        self.tab_widget = QTabWidget()
        self.watermark_tab = WatermarkTab()
        self.merge_tab = MergeTab()
        self.batch_tab = BatchProcessTab()

        self.tab_widget.addTab(self.watermark_tab, "Add Watermark")
        self.tab_widget.addTab(self.merge_tab, "Merge PDFs")
        self.tab_widget.addTab(self.batch_tab, "Batch Process")

        layout.addWidget(self.tab_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        central_widget.setLayout(layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Connect signals
        self.watermark_tab.status_changed.connect(self._on_status_changed)
        self.watermark_tab.progress_changed.connect(self._on_progress_changed)
        self.watermark_tab.error_occurred.connect(self._on_error)

        self.merge_tab.status_changed.connect(self._on_status_changed)
        self.merge_tab.progress_changed.connect(self._on_progress_changed)
        self.merge_tab.error_occurred.connect(self._on_error)

        self.batch_tab.status_changed.connect(self._on_status_changed)
        self.batch_tab.progress_changed.connect(self._on_progress_changed)
        self.batch_tab.error_occurred.connect(self._on_error)

    @pyqtSlot(str)
    def _on_status_changed(self, status: str) -> None:
        """Update status bar."""
        self.status_bar.showMessage(status)

    @pyqtSlot(int)
    def _on_progress_changed(self, progress: int) -> None:
        """Update progress bar."""
        if progress == 0:
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)

    @pyqtSlot(str)
    def _on_error(self, error: str) -> None:
        """Show error message."""
        QMessageBox.critical(self, "Error", error)
        self.progress_bar.setVisible(False)


def main():
    """Main entry point for the GUI application."""
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
