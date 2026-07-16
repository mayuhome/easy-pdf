from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from easy_pdf.domain.errors import TaskNotFoundError
from easy_pdf.domain.models import Task, TaskStatus
from easy_pdf.storage.project_store import ProjectStore


class TaskService:
    def __init__(self, store: ProjectStore) -> None:
        self.store = store
        self._tasks: dict[str, Task] = {}

    def submit_task(self, task_type: str, payload: dict, priority: int = 5) -> Task:
        now = datetime.now(timezone.utc).isoformat()
        task = Task(
            task_id=f"task_{uuid4().hex[:12]}",
            task_type=task_type,
            status=TaskStatus.QUEUED,
            progress=0.0,
            payload=payload,
            logs=["queued"],
        )
        self._tasks[task.task_id] = task
        self.store.save_task(
            {
                "id": task.task_id,
                "task_type": task.task_type,
                "status": task.status.value,
                "priority": priority,
                "progress": task.progress,
                "payload": task.payload,
                "logs": task.logs,
                "result_ref": task.result_ref,
                "error": task.error,
                "created_at": now,
            }
        )
        return task

    def mark_running(self, task_id: str) -> None:
        task = self.get_task(task_id)
        task.status = TaskStatus.RUNNING
        task.logs.append("running")
        self._persist(task)

    def mark_done(self, task_id: str, result_ref: str | None = None) -> None:
        task = self.get_task(task_id)
        task.status = TaskStatus.DONE
        task.progress = 1.0
        task.result_ref = result_ref
        task.logs.append("done")
        self._persist(task)

    def cancel_task(self, task_id: str) -> bool:
        task = self.get_task(task_id)
        if task.status in {TaskStatus.DONE, TaskStatus.FAILED}:
            return False
        task.status = TaskStatus.CANCELED
        task.logs.append("canceled")
        self._persist(task)
        return True

    def get_task(self, task_id: str) -> Task:
        task = self._tasks.get(task_id)
        if task:
            return task

        data = self.store.get_task(task_id)
        if not data:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        task = Task(
            task_id=data["id"],
            task_type=data["task_type"],
            status=TaskStatus(data["status"]),
            progress=float(data.get("progress", 0.0)),
            payload=data.get("payload", {}),
            logs=data.get("logs", []),
            result_ref=data.get("result_ref"),
            error=data.get("error"),
        )
        self._tasks[task.task_id] = task
        return task

    def _persist(self, task: Task) -> None:
        self.store.save_task(
            {
                "id": task.task_id,
                "task_type": task.task_type,
                "status": task.status.value,
                "progress": task.progress,
                "payload": task.payload,
                "logs": task.logs,
                "result_ref": task.result_ref,
                "error": task.error,
            }
        )
