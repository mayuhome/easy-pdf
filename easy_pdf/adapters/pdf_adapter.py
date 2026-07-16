from __future__ import annotations

from pathlib import Path
from typing import Any

import fitz
import pikepdf


class PdfAdapter:
    """PDF adapter backed by PyMuPDF for core read/edit operations."""

    DEFAULT_MARKER_WORDS = (
        "watermark",
        "confidential",
        "sample",
        "draft",
        "copy",
    )

    def exists(self, path: str) -> bool:
        return Path(path).exists()

    def estimate_page_count(self, path: str) -> int:
        if not self.exists(path):
            return 0
        with fitz.open(path) as doc:
            return doc.page_count

    def is_encrypted(self, path: str) -> bool:
        with fitz.open(path) as doc:
            return doc.needs_pass

    def duplicate_file(self, input_path: str, output_path: str) -> None:
        try:
            with pikepdf.open(input_path) as pdf:
                pdf.save(output_path)
            return
        except Exception:
            # Keep a robust fallback path for malformed files.
            data = Path(input_path).read_bytes()
            Path(output_path).write_bytes(data)

    def scan_text_watermark_candidates(
        self,
        path: str,
        page_indices: list[int],
        sensitivity: int = 3,
    ) -> list[dict[str, Any]]:
        """Return watermark-like text candidates with bbox for each scanned page."""
        size_floor = max(10.0, 24.0 - float(sensitivity * 2))
        candidates: list[dict[str, Any]] = []

        with fitz.open(path) as doc:
            for page_index in page_indices:
                page = doc.load_page(page_index)
                text_dict = page.get_text("dict")
                for block in text_dict.get("blocks", []):
                    if block.get("type") != 0:
                        continue
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = (span.get("text") or "").strip()
                            if not text:
                                continue
                            if not self._looks_like_watermark_text(text):
                                continue
                            if float(span.get("size", 0.0)) < size_floor:
                                continue

                            bbox = span.get("bbox")
                            if not bbox or len(bbox) != 4:
                                continue

                            candidates.append(
                                {
                                    "page_index": page_index,
                                    "text": text,
                                    "bbox": {
                                        "x": float(bbox[0]),
                                        "y": float(bbox[1]),
                                        "w": float(bbox[2] - bbox[0]),
                                        "h": float(bbox[3] - bbox[1]),
                                    },
                                }
                            )
        return candidates

    def redact_regions_inplace(self, path: str, regions: dict[int, list[dict[str, float]]]) -> int:
        """Apply white redaction rectangles in-place and return changed page count."""
        changed_pages = 0
        target = Path(path)
        temp_path = str(target.with_suffix(target.suffix + ".tmp"))
        with fitz.open(path) as doc:
            for page_index, rects in regions.items():
                if not rects:
                    continue
                page = doc.load_page(page_index)
                for rect_data in rects:
                    rect = fitz.Rect(
                        rect_data["x"],
                        rect_data["y"],
                        rect_data["x"] + rect_data["w"],
                        rect_data["y"] + rect_data["h"],
                    )
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                changed_pages += 1

            if changed_pages:
                doc.save(temp_path, garbage=4, deflate=True)
        if changed_pages:
            Path(temp_path).replace(target)
        return changed_pages

    def _looks_like_watermark_text(self, text: str) -> bool:
        lowered = text.lower()
        if any(token in lowered for token in self.DEFAULT_MARKER_WORDS):
            return True
        letters = [ch for ch in text if ch.isalpha()]
        if len(letters) >= 6:
            upper_ratio = sum(ch.isupper() for ch in letters) / len(letters)
            if upper_ratio > 0.8:
                return True
        return False
