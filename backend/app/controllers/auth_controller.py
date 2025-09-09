from flask import Response
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask_smorest import Blueprint

from ..schemas import AuthReqSchema
from ..services import AuthService
from ..utils import unlogged_required

auth_bp = Blueprint(
    "Authentication API",
    "auth_bp",
    url_prefix="/api/auth",
    description="Endpoints for authentication and authorization",
)


@auth_bp.route("/login", methods=["POST"])
@auth_bp.arguments(AuthReqSchema, as_kwargs=True)
@auth_bp.response(204, description="Successful login")
@unlogged_required()
def login(email: str, password: str):
    user = AuthService.login(email, password)
    access_token = create_access_token(
        identity=user.uuid, additional_claims={"role": user.role.value}
    )
    response = Response(status=204, content_type="application/json")
    set_access_cookies(response, access_token)
    return response


@auth_bp.route("/logout", methods=["POST"])
@auth_bp.response(204, description="Successful logout")
@jwt_required()
def logout():
    response = Response(status=204, content_type="application/json")
    unset_jwt_cookies(response)
    return response
