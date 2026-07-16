from __future__ import annotations

from uuid import uuid4

from easy_pdf.domain.models import OperationResult


class WatermarkApplyService:
    def apply_text_watermark(
        self,
        document_id: str,
        text: str,
        page_range: str = "1-*",
    ) -> OperationResult:
        del document_id, text, page_range
        return OperationResult(
            operation_id=f"op_{uuid4().hex[:12]}",
            success=True,
            changed_pages=1,
        )

    def apply_image_watermark(
        self,
        document_id: str,
        image_path: str,
        page_range: str = "1-*",
    ) -> OperationResult:
        del document_id, image_path, page_range
        return OperationResult(
            operation_id=f"op_{uuid4().hex[:12]}",
            success=True,
            changed_pages=1,
        )
