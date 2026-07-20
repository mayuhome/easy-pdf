from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WatermarkKind(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    ANNOTATION = "annotation"
    RASTER = "raster"
    FORM = "form"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass(slots=True)
class Rect:
    x: float
    y: float
    w: float
    h: float


@dataclass(slots=True)
class DocumentSession:
    document_id: str
    path: str
    page_count: int = 0
    encrypted: bool = False
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WatermarkCandidate:
    candidate_id: str
    page_index: int
    kind: WatermarkKind
    bbox: Rect
    confidence: float
    removable: bool
    preview_text: str = ""
    pattern_group_id: str | None = None


@dataclass(slots=True)
class OperationResult:
    operation_id: str
    success: bool
    changed_pages: int
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Task:
    task_id: str
    task_type: str
    status: TaskStatus
    progress: float = 0.0
    payload: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    result_ref: str | None = None
    error: dict[str, Any] | None = None
