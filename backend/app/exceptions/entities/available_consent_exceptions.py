from werkzeug.exceptions import BadRequest, NotFound, UnprocessableEntity
from werkzeug.http import HTTP_STATUS_CODES


class AvailableConsentNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]


class AvailableConsentApplicationMismatchException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = BadRequest.code
        self.status = HTTP_STATUS_CODES[self.code]


class AvailableConsentEmptyListException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = UnprocessableEntity.code
        self.status = HTTP_STATUS_CODES[self.code]


class AvailableConsentWrongListException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = UnprocessableEntity.code
        self.status = HTTP_STATUS_CODES[self.code]
