from __future__ import annotations

from uuid import uuid4

from easy_pdf.domain.models import OperationResult
from easy_pdf.services.document_service import DocumentService


class PageEditService:
    def __init__(self, document_service: DocumentService) -> None:
        self.document_service = document_service

    def delete_pages(self, document_id: str, pages: list[int]) -> OperationResult:
        doc = self.document_service.require(document_id)
        doc.page_count = max(0, doc.page_count - len(set(pages)))
        return OperationResult(
            operation_id=f"op_{uuid4().hex[:12]}",
            success=True,
            changed_pages=len(set(pages)),
        )

    def rotate_pages(self, document_id: str, pages: list[int], degree: int) -> OperationResult:
        del document_id, degree
        return OperationResult(
            operation_id=f"op_{uuid4().hex[:12]}",
            success=True,
            changed_pages=len(set(pages)),
        )
