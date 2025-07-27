from werkzeug.exceptions import Forbidden, Unauthorized
from werkzeug.http import HTTP_STATUS_CODES


class ExpiredJWTException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Forbidden.code
        self.status = HTTP_STATUS_CODES.get(self.code, "Unknown Error")


class InvalidJWTException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Unauthorized.code
        self.status = HTTP_STATUS_CODES.get(self.code, "Unknown Error")


class MissingJWTException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Unauthorized.code
        self.status = HTTP_STATUS_CODES.get(self.code, "Unknown Error")
