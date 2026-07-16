class EasyPdfError(Exception):
    """Base application error."""

    code = "SYS_000"


class DocumentNotFoundError(EasyPdfError):
    code = "DOC_001"


class InvalidPasswordError(EasyPdfError):
    code = "DOC_002"


class InvalidRequestError(EasyPdfError):
    code = "REQ_001"


class CandidateNotFoundError(EasyPdfError):
    code = "WM_001"


class TaskNotFoundError(EasyPdfError):
    code = "TASK_001"


class PDFOperationError(EasyPdfError):
    """Error during PDF operations."""

    code = "PDF_001"
