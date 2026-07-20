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
        self._candidate_payload_index: dict[str, dict[str, dict[str, object]]] = {}

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
        structural = self.document_service.adapter.scan_structural_watermark_candidates(
            doc.path,
            page_indices=page_indices,
        )

        text_frequency = Counter(item["text"].strip().lower() for item in scanned)
        text_page_frequency: dict[str, set[int]] = defaultdict(set)
        edge_frequency: Counter[str] = Counter()
        for item in scanned:
            token = item["text"].strip().lower()
            text_page_frequency[token].add(int(item["page_index"]))
            if item.get("near_edge"):
                edge_frequency[token] += 1

        candidates: list[WatermarkCandidate] = []
        candidate_payloads: dict[str, dict[str, object]] = {}
        for item in scanned:
            token = item["text"].strip().lower()
            repeat_count = text_frequency[token]
            repeat_pages = len(text_page_frequency[token])
            edge_ratio = edge_frequency[token] / max(repeat_count, 1)
            is_repeated_edge_text = (
                item.get("source") == "line"
                and len(token) >= 8
                and repeat_pages >= max(2, sensitivity)
                and edge_ratio >= 0.6
            )
            is_styled_text = item.get("source") == "span"

            if not (is_styled_text or is_repeated_edge_text):
                continue

            safe_to_redact = self._is_text_candidate_safely_removable(item)

            repeat_bonus = min(0.2, 0.02 * max(0, repeat_count - 1))
            page_bonus = min(0.2, 0.05 * max(0, repeat_pages - 1))
            edge_bonus = 0.08 if is_repeated_edge_text else 0.0
            confidence = min(0.99, 0.62 + repeat_bonus + page_bonus + edge_bonus)
            stable_id = self._stable_candidate_id(item["page_index"], token, item["bbox"])
            candidates.append(
                WatermarkCandidate(
                    candidate_id=stable_id,
                    page_index=int(item["page_index"]),
                    kind=WatermarkKind.TEXT,
                    bbox=Rect(**item["bbox"]),
                    confidence=confidence,
                    removable=safe_to_redact,
                    preview_text=item["text"].strip(),
                    pattern_group_id=f"pg_{abs(hash(token)) % 100000:05d}",
                )
            )
            candidate_payloads[stable_id] = item

        for item in structural:
            token = str(item.get("xobject_name", item.get("text", "watermark"))).lower()
            stable_id = self._stable_candidate_id(item["page_index"], token, item["bbox"])
            candidates.append(
                WatermarkCandidate(
                    candidate_id=stable_id,
                    page_index=int(item["page_index"]),
                    kind=WatermarkKind.FORM,
                    bbox=Rect(**item["bbox"]),
                    confidence=0.99,
                    removable=False,
                    preview_text=str(item.get("text", "Watermark")).strip(),
                    pattern_group_id=f"pg_{abs(hash(token)) % 100000:05d}",
                )
            )
            candidate_payloads[stable_id] = item

        self._candidate_index[document_id] = candidates
        self._candidate_payload_index[document_id] = candidate_payloads
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
        candidate_payloads = self._candidate_payload_index.get(document_id, {})
        for cid in candidate_ids:
            if cid not in candidates:
                raise CandidateNotFoundError(f"Unknown watermark candidate: {cid}")

        doc = self.document_service.require(document_id)
        page_regions: dict[int, list[dict[str, float]]] = defaultdict(list)
        page_xobjects: dict[int, list[str]] = defaultdict(list)
        for cid in candidate_ids:
            c = candidates[cid]
            payload = candidate_payloads.get(cid, {})
            if c.kind == WatermarkKind.FORM and "xobject_name" in payload:
                page_xobjects[c.page_index].append(str(payload["xobject_name"]))
                continue

            if not self._should_redact_text_candidate(c.page_index, payload, page_xobjects):
                continue

            page_regions[c.page_index].append(
                {"x": c.bbox.x, "y": c.bbox.y, "w": c.bbox.w, "h": c.bbox.h}
            )

        changed_pages = 0
        warnings: list[str] = []
        if structural_delete:
            structural_changes = self.document_service.adapter.remove_watermark_xobjects_inplace(
                doc.path,
                page_xobjects,
            )
            text_changes = self.document_service.adapter.redact_regions_inplace(doc.path, page_regions)
            if structural_changes or text_changes:
                changed_pages = len(
                    {
                        page_index
                        for page_index, names in page_xobjects.items()
                        if names
                    }
                    |
                    {
                        page_index
                        for page_index, rects in page_regions.items()
                        if rects
                    }
                )
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

    @staticmethod
    def _should_redact_text_candidate(
        page_index: int,
        payload: dict[str, object],
        page_xobjects: dict[int, list[str]],
    ) -> bool:
        if not page_xobjects.get(page_index):
            return True

        bbox = payload.get("bbox")
        page_height = payload.get("page_height")
        if not isinstance(bbox, dict) or not isinstance(page_height, (int, float)):
            return False

        y = float(bbox.get("y", 0.0))
        h = float(bbox.get("h", 0.0))
        bottom = y + h

        # On pages where a structural watermark object exists, avoid redacting
        # top-edge text because it overlaps real title/body content in sample PDFs.
        return bottom >= float(page_height) * 0.9

    @staticmethod
    def _is_text_candidate_safely_removable(item: dict[str, object]) -> bool:
        bbox = item.get("bbox")
        page_height = item.get("page_height")
        if not isinstance(bbox, dict) or not isinstance(page_height, (int, float)):
            return False

        y = float(bbox.get("y", 0.0))
        h = float(bbox.get("h", 0.0))
        bottom = y + h
        source = str(item.get("source", ""))

        if source == "span":
            return True

        return bottom >= float(page_height) * 0.9
