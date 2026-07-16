from __future__ import annotations

from uuid import uuid4

from easy_pdf.domain.errors import CandidateNotFoundError
from easy_pdf.domain.models import OperationResult, Rect, WatermarkCandidate, WatermarkKind
from easy_pdf.services.document_service import DocumentService


class WatermarkService:
    def __init__(self, document_service: DocumentService) -> None:
        self.document_service = document_service
        self._candidate_index: dict[str, list[WatermarkCandidate]] = {}

    def detect_watermarks(
        self,
        document_id: str,
        mode: str = "hybrid",
        page_range: str = "1-*",
        sensitivity: int = 3,
    ) -> list[WatermarkCandidate]:
        del mode, page_range, sensitivity
        doc = self.document_service.require(document_id)
        candidates: list[WatermarkCandidate] = []

        # Placeholder rule: create one synthetic candidate per first 3 pages.
        for idx in range(min(3, doc.page_count)):
            candidates.append(
                WatermarkCandidate(
                    candidate_id=f"wm_{uuid4().hex[:8]}",
                    page_index=idx,
                    kind=WatermarkKind.TEXT,
                    bbox=Rect(x=100, y=120, w=300, h=80),
                    confidence=0.8,
                    removable=True,
                    pattern_group_id="pg_demo",
                )
            )
        self._candidate_index[document_id] = candidates
        return candidates

    def remove_watermarks(
        self,
        document_id: str,
        candidate_ids: list[str],
        structural_delete: bool = True,
        region_inpaint: bool = True,
    ) -> OperationResult:
        del structural_delete, region_inpaint
        candidates = {c.candidate_id: c for c in self._candidate_index.get(document_id, [])}
        for cid in candidate_ids:
            if cid not in candidates:
                raise CandidateNotFoundError(f"Unknown watermark candidate: {cid}")

        return OperationResult(
            operation_id=f"op_{uuid4().hex[:12]}",
            success=True,
            changed_pages=len({candidates[c].page_index for c in candidate_ids}),
            warnings=[],
        )
