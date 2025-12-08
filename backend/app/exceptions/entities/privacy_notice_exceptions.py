from werkzeug.exceptions import Conflict, NotFound
from werkzeug.http import HTTP_STATUS_CODES


class PrivacyNoticeNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]


class PrivacyNoticeAlreadyExists(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Conflict.code
        self.status = HTTP_STATUS_CODES[self.code]
