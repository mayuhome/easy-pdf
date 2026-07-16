# Data Schema (SQLite + Project File)

## SQLite Tables (v0.1)

### schema_migrations
- version INTEGER PRIMARY KEY
- name TEXT NOT NULL
- applied_at TEXT NOT NULL

### documents
- id TEXT PRIMARY KEY
- file_path TEXT NOT NULL
- file_name TEXT NOT NULL
- page_count INTEGER NOT NULL
- encrypted INTEGER NOT NULL DEFAULT 0
- opened_at TEXT NOT NULL
- updated_at TEXT NOT NULL

### tasks
- id TEXT PRIMARY KEY
- task_type TEXT NOT NULL
- status TEXT NOT NULL
- progress REAL NOT NULL DEFAULT 0
- payload_json TEXT NOT NULL
- created_at TEXT NOT NULL
- started_at TEXT NULL
- finished_at TEXT NULL

## Project File (planned)

`project.json`

```json
{
  "schemaVersion": 1,
  "projectId": "proj_xxx",
  "source": {
    "filePath": "/abs/path/file.pdf",
    "sha256": "..."
  },
  "working": {
    "documentId": "doc_xxx",
    "currentPage": 1,
    "zoom": 1.0
  },
  "history": {
    "operations": [],
    "undoCursor": 0
  }
}
```

## Migration Rules

1. Additive first: add columns before removing old fields.
2. Keep compatibility by `schemaVersion`.
3. Auto-upgrade in memory, then persist to latest format.
4. Fail-safe: if migration fails, open in read-only mode.
