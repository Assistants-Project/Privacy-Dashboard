from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.http import HTTP_STATUS_CODES


class QuestionNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]


class InvalidAnswerContentException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = BadRequest.code
        self.status = HTTP_STATUS_CODES[self.code]


class MissingRequiredAnswerException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = BadRequest.code
        self.status = HTTP_STATUS_CODES[self.code]
