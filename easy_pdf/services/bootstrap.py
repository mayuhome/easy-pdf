from __future__ import annotations

from pathlib import Path

from easy_pdf.adapters.pdf_adapter import PdfAdapter
from easy_pdf.services.document_service import DocumentService
from easy_pdf.services.page_edit_service import PageEditService
from easy_pdf.services.task_service import TaskService
from easy_pdf.services.watermark_apply_service import WatermarkApplyService
from easy_pdf.services.watermark_service import WatermarkService
from easy_pdf.storage.project_store import ProjectStore


class AppContainer:
    def __init__(self, workdir: str | None = None) -> None:
        base = Path(workdir or Path.home() / ".easy-pdf")
        self.store = ProjectStore(str(base / "easy_pdf.db"))
        self.store.init()

        adapter = PdfAdapter()
        self.document_service = DocumentService(adapter, self.store)
        self.watermark_service = WatermarkService(self.document_service)
        self.page_edit_service = PageEditService(self.document_service)
        self.watermark_apply_service = WatermarkApplyService()
        self.task_service = TaskService(self.store)
