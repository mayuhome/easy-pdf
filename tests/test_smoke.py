from pathlib import Path

import fitz

from easy_pdf.services.bootstrap import AppContainer


def test_health_bootstrap() -> None:
    container = AppContainer(workdir="/tmp/easy-pdf-test")
    assert container.document_service is not None
    assert container.task_service is not None


def test_document_rehydrate_from_store(tmp_path: Path) -> None:
    pdf = tmp_path / "demo.pdf"
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), "demo", fontsize=12)
        doc.save(str(pdf))

    c1 = AppContainer(workdir=str(tmp_path / "work"))
    doc = c1.document_service.open_document(str(pdf))

    c2 = AppContainer(workdir=str(tmp_path / "work"))
    summary = c2.document_service.get_summary(doc.document_id)
    assert summary["document_id"] == doc.document_id
    assert summary["file_name"] == "demo.pdf"


def test_task_persist_and_load(tmp_path: Path) -> None:
    c1 = AppContainer(workdir=str(tmp_path / "work"))
    task = c1.task_service.submit_task(task_type="detect", payload={"document_id": "doc_x"})
    c1.task_service.mark_running(task.task_id)
    c1.task_service.mark_done(task.task_id, result_ref="ok")

    c2 = AppContainer(workdir=str(tmp_path / "work"))
    loaded = c2.task_service.get_task(task.task_id)
    assert loaded.status.value == "done"
    assert loaded.result_ref == "ok"


def test_detect_and_remove_watermark_on_real_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "watermark.pdf"
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), "Body text", fontsize=12)
        page.insert_text((120, 280), "CONFIDENTIAL", fontsize=42)
        doc.save(str(pdf_path))

    container = AppContainer(workdir=str(tmp_path / "work"))
    opened = container.document_service.open_document(str(pdf_path))
    candidates = container.watermark_service.detect_watermarks(opened.document_id)
    assert candidates, "Expected at least one watermark candidate"

    result = container.watermark_service.remove_watermarks(
        opened.document_id,
        candidate_ids=[candidates[0].candidate_id],
    )
    assert result.success is True
    assert result.changed_pages >= 1
