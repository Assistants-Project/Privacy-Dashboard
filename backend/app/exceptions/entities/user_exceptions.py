from werkzeug.exceptions import Forbidden, NotFound, Unauthorized
from werkzeug.http import HTTP_STATUS_CODES


class UserNotFoundException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = NotFound.code
        self.status = HTTP_STATUS_CODES.get(self.code, "Unknown Error")


class WrongUserCredentialsException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Unauthorized.code
        self.status = HTTP_STATUS_CODES.get(self.code, "Unknown Error")


class WrongUserRoleException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = Forbidden.code
        self.status = HTTP_STATUS_CODES.get(self.code, "Unknown Error")
