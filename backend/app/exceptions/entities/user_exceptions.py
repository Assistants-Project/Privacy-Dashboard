from werkzeug.exceptions import BadRequest, Forbidden, NotFound, Unauthorized
from werkzeug.http import HTTP_STATUS_CODES


class UserNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES[self.code]


class WrongUserCredentialsException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Unauthorized.code
        self.status = HTTP_STATUS_CODES[self.code]


class WrongUserRoleException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Forbidden.code
        self.status = HTTP_STATUS_CODES[self.code]


class WrongUserUuidException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = BadRequest.code
        self.status = HTTP_STATUS_CODES[self.code]


class UnloggedUserException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Unauthorized.code
        self.status = HTTP_STATUS_CODES[self.code]
