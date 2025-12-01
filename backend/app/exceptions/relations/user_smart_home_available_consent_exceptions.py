from werkzeug.exceptions import Conflict, InternalServerError
from werkzeug.http import HTTP_STATUS_CODES


class UserSmartHomeAvailableConsentCreationException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = InternalServerError.code
        self.status = HTTP_STATUS_CODES[self.code]


class UserSmartHomeAvailableConsentAlreadyCreatedException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Conflict.code
        self.status = HTTP_STATUS_CODES[self.code]
