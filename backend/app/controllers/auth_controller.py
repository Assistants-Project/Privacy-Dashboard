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

from flask import current_app
from ..utils import smartotum_required

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

    # OLD
    # user = AuthService.login(email, password)
    # access_token = create_access_token(
    #     identity=user.uuid, additional_claims={"role": user.role.value}
    # )
    # response = Response(status=204, content_type="application/json")
    # set_access_cookies(response, access_token)
    # return response

    result = AuthService.login(email,password)

    user = result["user"]
    access_token = result["access_token"]
    refresh_token = result["refresh_token"]

    response = Response(status=204, content_type="application/json")

    
    secure_cookie = current_app.config.get("JWT_COOKIE_SECURE", True)
    response.set_cookie(
        "st_access_token",
        access_token,
        httponly=True,
        secure=secure_cookie,
        samesite="None" if secure_cookie else "Lax",
        path="/",
    )

    #only to test we send the refresh token, will have to save it somewhere
    response.set_cookie(
        "st_refresh_token",
        refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="None" if secure_cookie else "Lax",
        path="/",
    )

    return response


@auth_bp.route("/logout", methods=["POST"])
@auth_bp.response(204, description="Successful logout")
@smartotum_required()
#@jwt_required()
def logout():

    response = Response(status=204, content_type="application/json")
    response.delete_cookie("st_access_token", path="/")
    response.delete_cookie("st_refresh_token", path="/")
    return response

    # OLD
    # response = Response(status=204, content_type="application/json")
    # unset_jwt_cookies(response)
    # return response
