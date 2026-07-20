from __future__ import annotations

import math
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

    def apply_text_watermark(
        self,
        input_path: str,
        output_path: str,
        text: str,
        opacity: float = 0.5,
        font_size: int = 24,
    ) -> None:
        """Write a text watermark to each page and save to a new file."""
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        safe_opacity = min(0.6, max(0.12, float(opacity)))
        safe_font_size = max(20.0, float(font_size))
        font_name, font_file = self._pick_watermark_font(text)
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Watermark text must not be empty")

        # Keep real output direction identical to preview: bottom-left -> top-right.
        angle_deg = -35.0
        angle_rad = math.radians(abs(angle_deg))
        cos_a = abs(math.cos(angle_rad))
        sin_a = abs(math.sin(angle_rad))
        margin_ratio = 0.08

        font = fitz.Font(fontname=font_name, fontfile=font_file)

        with fitz.open(input_path) as doc:
            for page in doc:
                page_w = float(page.rect.width)
                page_h = float(page.rect.height)
                max_rot_w = page_w * (1.0 - margin_ratio * 2.0)
                max_rot_h = page_h * (1.0 - margin_ratio * 2.0)

                # Start from requested size, then shrink to fit transformed bounds.
                watermark_size = min(safe_font_size, min(page_w, page_h) * 0.28)
                watermark_size = max(20.0, watermark_size)

                text_w = font.text_length(clean_text, fontsize=watermark_size)
                text_h = watermark_size
                rot_w = text_w * cos_a + text_h * sin_a
                rot_h = text_w * sin_a + text_h * cos_a

                fit_scale = min(
                    1.0,
                    max_rot_w / max(rot_w, 1e-6),
                    max_rot_h / max(rot_h, 1e-6),
                )
                watermark_size = max(12.0, watermark_size * fit_scale)

                text_w = font.text_length(clean_text, fontsize=watermark_size)
                center = fitz.Point(page_w * 0.5, page_h * 0.5)
                point = fitz.Point(center.x - text_w * 0.5, center.y + watermark_size * 0.35)
                morph_matrix = fitz.Matrix(1, 1).prerotate(angle_deg)
                page.insert_text(
                    point,
                    clean_text,
                    fontsize=watermark_size,
                    fontname=font_name,
                    fontfile=font_file,
                    color=(0.72, 0.72, 0.72),
                    fill_opacity=safe_opacity,
                    morph=(center, morph_matrix),
                    overlay=True,
                )
            doc.save(str(target), garbage=4, deflate=True)

    @staticmethod
    def _pick_watermark_font(text: str) -> tuple[str, str | None]:
        """Pick a font that can render user text reliably, including CJK on macOS."""
        has_non_ascii = any(ord(ch) > 127 for ch in text)
        if not has_non_ascii:
            # Built-in Times-Italic for common Latin text.
            return "tiro", None

        # Prefer common macOS CJK fonts to avoid "..." when rendering Chinese text.
        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return "cjk", candidate

        # Fallback for environments without the CJK system fonts above.
        return "helv", None

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
