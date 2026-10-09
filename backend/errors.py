"""Transport-independent failures raised by application services."""
from typing import Any, Mapping, Optional


class ApplicationError(Exception):
    """A service failure translated to the existing HTTP contract by the API."""

    def __init__(self, status_code: int, detail: Any, headers: Optional[Mapping[str, str]] = None):
        super().__init__(str(detail))
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
