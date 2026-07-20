from __future__ import annotations

import json

import typer
from rich import print

from easy_pdf.domain.errors import EasyPdfError
from easy_pdf.services.bootstrap import AppContainer

app = typer.Typer(help="easy-pdf CLI")
container = AppContainer()


def _emit(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


@app.command("health")
def health() -> None:
    _emit({"ok": True, "name": "easy-pdf", "version": "0.1.0"})


@app.command("open")
def open_document(path: str, password: str = "") -> None:
    doc = container.document_service.open_document(path=path, password=password or None)
    _emit(
        {
            "ok": True,
            "data": {
                "documentId": doc.document_id,
                "path": doc.path,
                "pageCount": doc.page_count,
                "encrypted": doc.encrypted,
            },
        }
    )


@app.command("summary")
def summary(document_id: str) -> None:
    _emit({"ok": True, "data": container.document_service.get_summary(document_id)})


@app.command("save")
def save(document_id: str, output_path: str, backup: bool = True) -> None:
    data = container.document_service.save_document(
        document_id=document_id,
        output_path=output_path,
        backup=backup,
    )
    _emit({"ok": True, "data": data})


@app.command("detect")
def detect(document_id: str, mode: str = "hybrid", page_range: str = "1-*", sensitivity: int = 3) -> None:
    result = container.watermark_service.detect_watermarks(
        document_id=document_id,
        mode=mode,
        page_range=page_range,
        sensitivity=sensitivity,
    )
    _emit(
        {
            "ok": True,
            "data": {
                "candidates": [
                    {
                        "candidateId": c.candidate_id,
                        "pageIndex": c.page_index,
                        "kind": c.kind.value,
                        "bbox": {"x": c.bbox.x, "y": c.bbox.y, "w": c.bbox.w, "h": c.bbox.h},
                        "confidence": c.confidence,
                        "removable": c.removable,
                        "previewText": c.preview_text,
                        "patternGroupId": c.pattern_group_id,
                    }
                    for c in result
                ]
            },
        }
    )


@app.command("remove")
def remove(document_id: str, candidate_ids: str) -> None:
    ids = [i.strip() for i in candidate_ids.split(",") if i.strip()]
    result = container.watermark_service.remove_watermarks(document_id=document_id, candidate_ids=ids)
    _emit(
        {
            "ok": True,
            "data": {
                "operationId": result.operation_id,
                "changedPages": result.changed_pages,
                "success": result.success,
            },
        }
    )


@app.command("task-submit")
def task_submit(task_type: str, document_id: str, candidate_ids: str = "") -> None:
    payload = {"document_id": document_id}
    if candidate_ids.strip():
        payload["candidate_ids"] = [i.strip() for i in candidate_ids.split(",") if i.strip()]

    task = container.task_service.submit_task(task_type=task_type, payload=payload)
    container.task_service.mark_running(task.task_id)

    if task_type == "detect":
        result = container.watermark_service.detect_watermarks(document_id=document_id)
        container.task_service.mark_done(task.task_id, result_ref=f"candidates:{len(result)}")
    elif task_type == "remove":
        ids = payload.get("candidate_ids", [])
        result = container.watermark_service.remove_watermarks(document_id=document_id, candidate_ids=ids)
        container.task_service.mark_done(task.task_id, result_ref=result.operation_id)
    else:
        container.task_service.mark_done(task.task_id, result_ref="noop")

    _emit(
        {
            "ok": True,
            "data": {
                "taskId": task.task_id,
                "taskType": task.task_type,
                "status": container.task_service.get_task(task.task_id).status.value,
            },
        }
    )


@app.command("task-status")
def task_status(task_id: str) -> None:
    task = container.task_service.get_task(task_id)
    _emit(
        {
            "ok": True,
            "data": {
                "taskId": task.task_id,
                "status": task.status.value,
                "progress": task.progress,
                "logs": task.logs,
                "resultRef": task.result_ref,
            },
        }
    )


@app.command("task-cancel")
def task_cancel(task_id: str) -> None:
    _emit({"ok": True, "data": {"canceled": container.task_service.cancel_task(task_id)}})


def main() -> None:
    try:
        app()
    except EasyPdfError as exc:
        _emit({"ok": False, "error": {"code": exc.code, "message": str(exc)}})
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
