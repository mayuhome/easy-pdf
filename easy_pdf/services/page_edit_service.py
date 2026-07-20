from __future__ import annotations

from pathlib import Path
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

    def merge_documents(self, input_paths: list[Path], output_path: Path) -> Path:
        """Merge input PDFs into output PDF path and return output path."""
        if not input_paths:
            raise ValueError("No PDF files to merge")

        self.document_service.adapter.merge_documents(
            input_paths=[str(path) for path in input_paths],
            output_path=str(output_path),
        )
        return output_path
