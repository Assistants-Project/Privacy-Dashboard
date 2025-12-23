from werkzeug.exceptions import InternalServerError, NotFound
from werkzeug.http import HTTP_STATUS_CODES


class QuestionnaireSubmissionException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = InternalServerError.code
        self.status = HTTP_STATUS_CODES[self.code]


class QuestionnaireNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]
