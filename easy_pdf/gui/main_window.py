"""Main window for the PDF toolkit GUI application."""

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from easy_pdf import __bugfix__, __version__
from easy_pdf.gui.tabs.batch_tab import BatchProcessTab
from easy_pdf.gui.tabs.merge_tab import MergeTab
from easy_pdf.gui.tabs.remove_watermark_tab import RemoveWatermarkTab
from easy_pdf.gui.tabs.watermark_tab import WatermarkTab
from easy_pdf.gui.theme import app_stylesheet


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Easy PDF - PDF Toolkit [{__bugfix__}]")
        self.setMinimumSize(1020, 720)
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setStyleSheet(app_stylesheet())

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(14)

        header = QWidget()
        header.setObjectName("AppHeader")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(4)

        header_title = QLabel("Easy PDF Toolkit")
        header_title.setObjectName("HeaderTitle")
        header_subtitle = QLabel("快速完成水印、合并与批量处理")
        header_subtitle.setObjectName("HeaderSubtitle")

        header_layout.addWidget(header_title)
        header_layout.addWidget(header_subtitle)
        header.setLayout(header_layout)
        layout.addWidget(header)

        tab_card = QWidget()
        tab_card.setObjectName("PageCard")
        tab_card_layout = QVBoxLayout()
        tab_card_layout.setContentsMargins(16, 16, 16, 14)
        tab_card_layout.setSpacing(10)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.watermark_tab = WatermarkTab()
        self.remove_watermark_tab = RemoveWatermarkTab()
        self.merge_tab = MergeTab()
        self.batch_tab = BatchProcessTab()

        self.tab_widget.addTab(self.watermark_tab, "Add Watermark")
        self.tab_widget.addTab(self.remove_watermark_tab, "Remove Watermark")
        self.tab_widget.addTab(self.merge_tab, "Merge PDFs")
        self.tab_widget.addTab(self.batch_tab, "Batch Process")

        tab_card_layout.addWidget(self.tab_widget)
        tab_card.setLayout(tab_card_layout)

        layout.addWidget(tab_card)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.footer_label = QLabel(f"Build {__version__} · {__bugfix__}")
        self.footer_label.setObjectName("FooterLabel")
        layout.addWidget(self.footer_label)

        central_widget.setLayout(layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Ready · {__bugfix__}")

        # Connect signals
        self.watermark_tab.status_changed.connect(self._on_status_changed)
        self.watermark_tab.progress_changed.connect(self._on_progress_changed)
        self.watermark_tab.error_occurred.connect(self._on_error)

        self.merge_tab.status_changed.connect(self._on_status_changed)
        self.merge_tab.progress_changed.connect(self._on_progress_changed)
        self.merge_tab.error_occurred.connect(self._on_error)

        self.remove_watermark_tab.status_changed.connect(self._on_status_changed)
        self.remove_watermark_tab.progress_changed.connect(self._on_progress_changed)
        self.remove_watermark_tab.error_occurred.connect(self._on_error)

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
