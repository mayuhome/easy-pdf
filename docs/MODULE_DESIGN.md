# Module Design (v0.1)

## Layers

1. UI Layer (future PySide6)
- Main window, preview canvas, thumbnail pane, operation panel.

2. Application Services
- `DocumentService`: open/summary/save and session lifecycle.
- `WatermarkService`: detect/remove watermark orchestration.
- `PageEditService`: delete/rotate/reorder page operations.
- `WatermarkApplyService`: apply text/image watermark operations.
- `TaskService`: local queue and status tracking.

3. Domain
- Entities: `DocumentSession`, `WatermarkCandidate`, `Task`.
- Value objects: `Rect`.
- Result objects: `OperationResult`.
- Errors with code mapping.

4. Adapters
- `PdfAdapter`: engine boundary for pikepdf/PyMuPDF integration.

5. Storage
- `ProjectStore`: sqlite schema bootstrap and migration entry.

## Extension Direction

- Keep service interface stable.
- Swap `PdfAdapter` placeholder with real implementations.
- Move heavy loops to Rust core via `pyo3` gradually.
- Add event bus for real-time UI progress updates.
