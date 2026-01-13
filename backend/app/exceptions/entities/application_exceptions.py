from werkzeug.exceptions import BadRequest, InternalServerError, NotFound
from werkzeug.http import HTTP_STATUS_CODES


class ApplicationNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]


class MissingPrivacyImpactAssessmentException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = BadRequest.code
        self.status = HTTP_STATUS_CODES[self.code]


class MissingTemplateException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = InternalServerError.code
        self.status = HTTP_STATUS_CODES[self.code]


class MissingValidationSchemaException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = InternalServerError.code
        self.status = HTTP_STATUS_CODES[self.code]


class InvalidPrivacyImpactAssessmentException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = BadRequest.code
        self.status = HTTP_STATUS_CODES[self.code]


class PrivacyImpactAssessmentNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]
