# easy-pdf

An offline-first desktop PDF tool foundation, designed for watermark removal and page editing.

## Goals

- Strong watermark removal quality with a two-path strategy:
  - Structural removal for removable watermark objects.
  - Region/image repair for rasterized watermark traces.
- Good local performance with a future Python + Rust hybrid architecture.
- Clean module boundaries so features can grow over time.

## Current Scope (v0.1 scaffold)

- Project architecture and API contracts are implemented.
- Basic service logic is in place for:
  - open/save summary
  - watermark candidate detection (rule-based placeholder)
  - page edit commands (delete/rotate/reorder placeholders)
  - watermark apply placeholders
  - local task queue state handling
- Documentation included:
  - `docs/API_CONTRACT.md`
  - `docs/MODULE_DESIGN.md`
  - `docs/DATA_SCHEMA.md`

## Quick Start

```bash
cd /Users/majade/projects/easy-pdf
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
# optional PDF runtime dependencies
pip install -e .[pdf]

easy-pdf health
```

## Build Package

Use the build script to generate both wheel and source distribution:

```bash
cd /Users/majade/projects/easy-pdf
chmod +x scripts/build.sh
./scripts/build.sh
```

Artifacts are generated under `dist/`.

## Release Check

Run end-to-end release validation (tests + build + clean install smoke check):

```bash
cd /Users/majade/projects/easy-pdf
chmod +x scripts/release.sh
./scripts/release.sh
```

Optional: skip tests if you only need packaging verification:

```bash
./scripts/release.sh --skip-tests
```

## CLI Examples

```bash
easy-pdf health
easy-pdf open /path/to/file.pdf
easy-pdf summary doc_123
easy-pdf save doc_123 /path/to/output.pdf

# task workflow
easy-pdf task-submit detect doc_123
easy-pdf task-status task_123
```

## Next Steps

- Integrate PySide6 UI shell.
- Add real PyMuPDF/pikepdf adapters for page ops and structural watermark deletion.
- Add Rust core for image inpaint and repeated watermark pattern matching.
