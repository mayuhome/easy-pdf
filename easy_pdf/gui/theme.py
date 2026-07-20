"""Centralized Qt stylesheet for a modern, Tailwind-inspired GUI."""


def app_stylesheet() -> str:
    """Return the global QSS stylesheet string."""
    return """
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    font-family: "PingFang SC", "Helvetica Neue", "Arial", sans-serif;
    color: #0f172a;
    font-size: 13px;
}

QWidget#AppHeader {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}

QLabel#HeaderTitle {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#HeaderSubtitle {
    font-size: 13px;
    color: #475569;
}

QLabel#FooterLabel {
    color: #64748b;
    font-size: 12px;
    padding: 2px 6px 0 6px;
}

QWidget#PageCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background: #e2e8f0;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    padding: 8px 16px;
    margin-right: 6px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #0f172a;
    border-color: #cbd5e1;
}

QTabBar::tab:hover:!selected {
    background: #dbeafe;
}

QGroupBox {
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 10px;
    padding: 14px 12px 12px 12px;
    background: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #334155;
}

QLabel#StepTitle {
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 6px;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
    border-radius: 10px;
    padding: 8px 14px;
    min-height: 34px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #94a3b8;
    border-color: #94a3b8;
    color: #f8fafc;
    min-height: 34px;
    padding: 8px 14px;
}

QPushButton#SecondaryBtn {
    background-color: #f1f5f9;
    color: #0f172a;
    border: 1px solid #cbd5e1;
}

QPushButton#SecondaryBtn:hover {
    background-color: #e2e8f0;
}

QLineEdit,
QListWidget,
QSpinBox {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 7px 10px;
    min-height: 32px;
    selection-background-color: #bfdbfe;
}

QLineEdit:focus,
QListWidget:focus,
QSpinBox:focus {
    border: 1px solid #2563eb;
}

QListWidget {
    min-height: 180px;
}

QListWidget::item {
    border: none;
    padding: 0;
}

QWidget#DetectionRow,
QWidget#DetectionInfoRow {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}

QLabel#DetectionRowLabel,
QLabel#DetectionInfoLabel {
    color: #0f172a;
}

QLabel#DetectionPreviewBadge {
    color: #92400e;
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
}

QCheckBox#DetectionRowCheckbox {
    spacing: 0;
    min-height: 18px;
}

QListWidget QScrollBar:vertical {
    background: #f1f5f9;
    width: 12px;
    margin: 6px 2px 6px 2px;
    border-radius: 6px;
}

QListWidget QScrollBar::handle:vertical {
    background: #94a3b8;
    min-height: 28px;
    border-radius: 6px;
}

QListWidget QScrollBar::handle:vertical:hover {
    background: #64748b;
}

QListWidget QScrollBar:horizontal {
    background: #f1f5f9;
    height: 12px;
    margin: 2px 6px 2px 6px;
    border-radius: 6px;
}

QListWidget QScrollBar::handle:horizontal {
    background: #94a3b8;
    min-width: 28px;
    border-radius: 6px;
}

QListWidget QScrollBar::handle:horizontal:hover {
    background: #64748b;
}

QListWidget QScrollBar::add-line,
QListWidget QScrollBar::sub-line,
QListWidget QScrollBar::add-page,
QListWidget QScrollBar::sub-page {
    background: transparent;
    border: none;
}

QCheckBox {
    spacing: 8px;
    color: #1e293b;
    font-weight: 500;
    min-height: 24px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #94a3b8;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background: #2563eb;
    border: 1px solid #1d4ed8;
}

QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background-color: #e2e8f0;
    text-align: center;
    min-height: 18px;
    font-weight: 600;
    color: #0f172a;
}

QProgressBar::chunk {
    background-color: #0ea5e9;
    border-radius: 7px;
}

QStatusBar {
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #334155;
}
"""
