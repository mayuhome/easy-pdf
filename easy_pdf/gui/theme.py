"""Centralized Qt stylesheet for a modern, Tailwind-inspired GUI."""


def app_stylesheet() -> str:
    """Return the global QSS stylesheet string."""
    return """
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    font-family: "SF Pro Text", "PingFang SC", "Helvetica Neue", sans-serif;
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

QCheckBox {
    spacing: 8px;
    color: #1e293b;
    font-weight: 500;
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
