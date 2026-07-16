# API Contract (v0.1)

This document defines the first usable command/service contract for easy-pdf.

## Response Envelope

Success:

```json
{
  "ok": true,
  "data": {}
}
```

Failure:

```json
{
  "ok": false,
  "error": {
    "code": "DOC_001",
    "message": "File not found"
  }
}
```

## Core Interfaces

### 1) openDocument

Input:

```json
{
  "path": "/abs/path/file.pdf",
  "password": "optional"
}
```

Output:

```json
{
  "documentId": "doc_xxx",
  "path": "/abs/path/file.pdf",
  "pageCount": 128,
  "encrypted": false
}
```

### 2) getDocumentSummary

Input:

```json
{
  "documentId": "doc_xxx"
}
```

Output:

```json
{
  "document_id": "doc_xxx",
  "path": "/abs/path/file.pdf",
  "page_count": 128,
  "size_bytes": 192843,
  "file_name": "file.pdf",
  "encrypted": false
}
```

### 3) detectWatermarks

Input:

```json
{
  "documentId": "doc_xxx",
  "mode": "hybrid",
  "pageRange": "1-*",
  "sensitivity": 3
}
```

Output:

```json
{
  "candidates": [
    {
      "candidateId": "wm_xxx",
      "pageIndex": 0,
      "kind": "text",
      "bbox": {"x": 100, "y": 120, "w": 300, "h": 80},
      "confidence": 0.8,
      "removable": true,
      "patternGroupId": "pg_demo"
    }
  ]
}
```

### 4) removeWatermarks

Input:

```json
{
  "documentId": "doc_xxx",
  "candidateIds": ["wm_1", "wm_2"],
  "structuralDelete": true,
  "regionInpaint": true
}
```

Output:

```json
{
  "operationId": "op_xxx",
  "changedPages": 2,
  "success": true
}
```

## Error Codes

- DOC_001: file not found
- DOC_002: invalid password
- REQ_001: invalid request
- WM_001: watermark candidate not found
- TASK_001: task not found
- SYS_000: unknown system error
