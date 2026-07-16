from __future__ import annotations

from pathlib import Path


class PdfAdapter:
    """Thin adapter placeholder. Real engine wiring will be added incrementally."""

    def exists(self, path: str) -> bool:
        return Path(path).exists()

    def estimate_page_count(self, path: str) -> int:
        # Placeholder logic. Replace with PyMuPDF real page count when dependency is available.
        if not self.exists(path):
            return 0
        return 1

    def duplicate_file(self, input_path: str, output_path: str) -> None:
        data = Path(input_path).read_bytes()
        Path(output_path).write_bytes(data)
