from werkzeug.exceptions import InternalServerError
from werkzeug.http import HTTP_STATUS_CODES


class DeviceSyncException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = InternalServerError.code
        self.status = HTTP_STATUS_CODES[self.code]
