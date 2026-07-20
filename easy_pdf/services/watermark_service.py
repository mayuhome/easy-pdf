from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
from pathlib import Path
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
        del mode
        doc = self.document_service.require(document_id)
        page_indices = self._parse_page_range(page_range, doc.page_count)
        scanned = self.document_service.adapter.scan_text_watermark_candidates(
            doc.path,
            page_indices=page_indices,
            sensitivity=sensitivity,
        )

        text_frequency = Counter(item["text"].strip().lower() for item in scanned)
        candidates: list[WatermarkCandidate] = []
        for item in scanned:
            token = item["text"].strip().lower()
            repeat_bonus = min(0.15, 0.03 * max(0, text_frequency[token] - 1))
            confidence = min(0.98, 0.7 + repeat_bonus)
            stable_id = self._stable_candidate_id(item["page_index"], token, item["bbox"])
            candidates.append(
                WatermarkCandidate(
                    candidate_id=stable_id,
                    page_index=int(item["page_index"]),
                    kind=WatermarkKind.TEXT,
                    bbox=Rect(**item["bbox"]),
                    confidence=confidence,
                    removable=True,
                    pattern_group_id=f"pg_{abs(hash(token)) % 100000:05d}",
                )
            )

        self._candidate_index[document_id] = candidates
        return candidates

    def apply_to_document(
        self,
        input_file: Path | str,
        output_file: Path | str,
        text: str,
        opacity: float = 0.5,
        font_size: int = 24,
    ) -> None:
        """Apply a text watermark to all pages and save to output file."""
        if not text.strip():
            raise ValueError("Watermark text must not be empty")

        self.document_service.adapter.apply_text_watermark(
            input_path=str(input_file),
            output_path=str(output_file),
            text=text,
            opacity=opacity,
            font_size=font_size,
        )

    def remove_watermarks(
        self,
        document_id: str,
        candidate_ids: list[str],
        structural_delete: bool = True,
        region_inpaint: bool = True,
    ) -> OperationResult:
        del region_inpaint
        if document_id not in self._candidate_index:
            self.detect_watermarks(document_id=document_id)

        candidates = {c.candidate_id: c for c in self._candidate_index.get(document_id, [])}
        for cid in candidate_ids:
            if cid not in candidates:
                raise CandidateNotFoundError(f"Unknown watermark candidate: {cid}")

        doc = self.document_service.require(document_id)
        page_regions: dict[int, list[dict[str, float]]] = defaultdict(list)
        for cid in candidate_ids:
            c = candidates[cid]
            page_regions[c.page_index].append(
                {"x": c.bbox.x, "y": c.bbox.y, "w": c.bbox.w, "h": c.bbox.h}
            )

        changed_pages = 0
        warnings: list[str] = []
        if structural_delete:
            changed_pages = self.document_service.adapter.redact_regions_inplace(doc.path, page_regions)
        else:
            warnings.append("structural_delete disabled; no edit applied")

        # Keep page count in sync in case later engines alter pagination.
        doc.page_count = self.document_service.adapter.estimate_page_count(doc.path)

        return OperationResult(
            operation_id=f"op_{uuid4().hex[:12]}",
            success=True,
            changed_pages=changed_pages,
            warnings=warnings,
        )

    @staticmethod
    def _parse_page_range(page_range: str, page_count: int) -> list[int]:
        if page_count <= 0:
            return []

        raw = page_range.strip()
        if not raw or raw == "1-*":
            return list(range(page_count))

        picked: set[int] = set()
        for part in (chunk.strip() for chunk in raw.split(",") if chunk.strip()):
            if "-" in part:
                start_s, end_s = part.split("-", 1)
                start = int(start_s) if start_s else 1
                end = page_count if end_s == "*" or not end_s else int(end_s)
                start = max(1, start)
                end = min(page_count, end)
                if start <= end:
                    picked.update(range(start - 1, end))
            else:
                idx = int(part)
                if 1 <= idx <= page_count:
                    picked.add(idx - 1)
        return sorted(picked)

    @staticmethod
    def _stable_candidate_id(page_index: int, token: str, bbox: dict[str, float]) -> str:
        raw = "|".join(
            [
                str(page_index),
                token,
                f"{bbox['x']:.2f}",
                f"{bbox['y']:.2f}",
                f"{bbox['w']:.2f}",
                f"{bbox['h']:.2f}",
            ]
        )
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
        return f"wm_{digest}"
