from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from easy_pdf.adapters.pdf_adapter import PdfAdapter
from easy_pdf.domain.errors import DocumentNotFoundError
from easy_pdf.domain.models import DocumentSession
from easy_pdf.storage.project_store import ProjectStore


class DocumentService:
    def __init__(self, adapter: PdfAdapter, store: ProjectStore) -> None:
        self.adapter = adapter
        self.store = store
        self._sessions: dict[str, DocumentSession] = {}

    def open_document(self, path: str, password: str | None = None) -> DocumentSession:
        del password  # Reserved for real encrypted-PDF support.
        if not self.adapter.exists(path):
            raise DocumentNotFoundError(f"File not found: {path}")

        doc_id = f"doc_{uuid4().hex[:12]}"
        session = DocumentSession(
            document_id=doc_id,
            path=path,
            page_count=self.adapter.estimate_page_count(path),
            encrypted=False,
            meta={"opened_at": datetime.now(timezone.utc).isoformat()},
        )
        self._sessions[doc_id] = session
        self.store.save_document(
            {
                "id": session.document_id,
                "file_path": session.path,
                "file_name": Path(session.path).name,
                "page_count": session.page_count,
                "encrypted": session.encrypted,
                "opened_at": session.meta.get("opened_at"),
            }
        )
        return session

    def get_summary(self, document_id: str) -> dict:
        session = self.require(document_id)
        stat = os.stat(session.path)
        return {
            "document_id": session.document_id,
            "path": session.path,
            "page_count": session.page_count,
            "size_bytes": stat.st_size,
            "file_name": Path(session.path).name,
            "encrypted": session.encrypted,
        }

    def save_document(self, document_id: str, output_path: str, backup: bool = True) -> dict:
        session = self.require(document_id)
        if backup and Path(output_path).exists():
            Path(output_path).rename(f"{output_path}.bak")
        self.adapter.duplicate_file(session.path, output_path)
        return {"output_path": output_path, "size_bytes": Path(output_path).stat().st_size}

    def require(self, document_id: str) -> DocumentSession:
        session = self._sessions.get(document_id)
        if session:
            return session

        db_doc = self.store.get_document(document_id)
        if not db_doc:
            raise DocumentNotFoundError(f"Document not found: {document_id}")

        session = DocumentSession(
            document_id=db_doc["id"],
            path=db_doc["file_path"],
            page_count=int(db_doc["page_count"]),
            encrypted=bool(db_doc["encrypted"]),
            meta={"opened_at": db_doc.get("opened_at")},
        )
        self._sessions[document_id] = session
        return session
