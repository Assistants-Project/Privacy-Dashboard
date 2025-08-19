from werkzeug.exceptions import NotFound
from werkzeug.http import HTTP_STATUS_CODES


class ApplicationNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]
