from functools import wraps

from flask import Response
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    verify_jwt_in_request,
)
from flask_smorest import Blueprint, abort

from ..schemas import AuthReqSchema
from ..services import AuthService


def unlogged_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return {"error": "Already logged in"}, 401
            except Exception:
                return fn(*args, **kwargs)

        return decorator

    return wrapper


auth_bp = Blueprint(
    "auth_bp", "auth_bp", url_prefix="/api/auth", description="Authentication API"
)


@auth_bp.route("/login", methods=["POST"])
@auth_bp.arguments(AuthReqSchema, as_kwargs=True)
@auth_bp.response(204)
@unlogged_required()
def login(email: str, password: str):
    try:
        user = AuthService.login(email, password)
        access_token = create_access_token(
            identity=user.email, additional_claims={"role": str(user.role)}
        )
        set_access_cookies(Response(status=204), access_token)
    except Exception as e:
        abort(401, message=str(e))
