from werkzeug.exceptions import GatewayTimeout, InternalServerError, ServiceUnavailable
from werkzeug.http import HTTP_STATUS_CODES


class SmartotumSyncException(Exception):
    """Raised when synchronizing Smartotum data fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = InternalServerError.code
        self.status = HTTP_STATUS_CODES[self.code]


class SmartotumServiceUnavailableException(Exception):
    """Raised when Smartotum service is unavailable or returns a server error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = ServiceUnavailable.code
        self.status = HTTP_STATUS_CODES[self.code]


class SmartotumTimeoutException(Exception):
    """Raised when Smartotum request times out."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = GatewayTimeout.code
        self.status = HTTP_STATUS_CODES[self.code]
