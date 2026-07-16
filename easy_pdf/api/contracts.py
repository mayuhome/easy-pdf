from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)
    recoverable: bool = True


class ApiResponse(BaseModel):
    ok: bool
    data: dict = Field(default_factory=dict)
    error: ErrorInfo | None = None


class OpenDocumentRequest(BaseModel):
    path: str
    password: str | None = None


class SaveDocumentRequest(BaseModel):
    document_id: str
    output_path: str
    optimize_level: str = "balanced"
    backup: bool = True


class DetectWatermarkRequest(BaseModel):
    document_id: str
    mode: str = "hybrid"
    page_range: str = "1-*"
    sensitivity: int = Field(default=3, ge=1, le=5)


class RemoveWatermarkRequest(BaseModel):
    document_id: str
    candidate_ids: list[str]
    structural_delete: bool = True
    region_inpaint: bool = True


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    logs: list[str] = Field(default_factory=list)
    result_ref: str | None = None
