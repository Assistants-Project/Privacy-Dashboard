from typing import Tuple

from flask import Response, jsonify


def global_error_handler(err: Exception) -> Tuple[Response, int]:
    """A global error handler function that catches all exceptions.

    It gets the `code`, `message` and `status` attributes from the exception
    if they exist, otherwise it uses default values.
    It returns a JSON response with the error information and the custom
    status code.

    Args:
        err: The exception that was raised, can be any custom exception subclassing `Exception`.

    Returns:
        A tuple containing the JSON response with the error information and the custom status code.
    """
    custom_code = getattr(err, "code", 500)
    custom_message = getattr(
        err, "message", "An internal error occurred. Please try again later."
    )
    custom_status = getattr(err, "status", "Internal Server Error")

    return jsonify(
        {
            "code": custom_code,
            "message": custom_message,
            "status": custom_status,
        }
    ), custom_code
