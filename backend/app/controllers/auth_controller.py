from flask import Response, current_app, jsonify
from flask_smorest import Blueprint

from ..schemas import AuthReqSchema, RegistrationReqSchema, UserResSchema
from ..services import AuthService
from ..utils import logged_in_required, unlogged_required, get_current_user_from_claims
from ..services.home_service import SmartHomeService

auth_bp = Blueprint(
    "Authentication API",
    "auth_bp",
    url_prefix="/api/auth",
    description="Endpoints for authentication and authorization",
)


@auth_bp.route("/register", methods=["POST"])
@auth_bp.arguments(RegistrationReqSchema, as_kwargs=True)
@unlogged_required()
def register(email, password, role, firstname, lastname):
    user = AuthService.register(email, password, role, firstname, lastname)
    response = jsonify(UserResSchema().dump(user))
    response.status_code = 201
    return response


@auth_bp.route("/login", methods=["POST"])
@auth_bp.arguments(AuthReqSchema, as_kwargs=True)
#@unlogged_required()
def login(email: str, password: str):
    result = AuthService.login(email, password)

    user = result.user
    access_token = result.access_token

    # try:
    #     SmartHomeService.update_database_for_user(user, access_token)
    # except Exception as exc:
    #     current_app.logger.warning(
    #         "Failed to sync Smartotum data during login: %s", exc
    #     )

    user_data = UserResSchema().dump(user)
    response = jsonify(user_data)

    secure_cookie = current_app.config.get("JWT_COOKIE_SECURE", True)
    response.set_cookie(
        "st_access_token",
        access_token,
        httponly=True,
        secure=secure_cookie,
        samesite="None" if secure_cookie else "Lax",
        path="/",
    )

    return response

@auth_bp.route("/current", methods=["GET"])
@auth_bp.response(200, UserResSchema(many=False))
@logged_in_required()
def current(current_user):
    return jsonify(UserResSchema().dump(current_user))

@auth_bp.route("/current", methods=["DELETE"])
@auth_bp.response(204, description="User Deleted Succefully")
@logged_in_required()
def delete_current(current_user):
    AuthService.delete_current_user(current_user)
    response = Response(status=204, content_type="application/json")
    secure_cookie = current_app.config.get("JWT_COOKIE_SECURE", True)
    response.delete_cookie(
        "st_access_token",
        path="/",
        httponly=True,
        secure=secure_cookie,
        samesite="None" if secure_cookie else "Lax",
    )
    return response

@auth_bp.route("/logout", methods=["POST"])
@auth_bp.response(204, description="Successful logout")
@logged_in_required()
def logout(current_user):
    response = Response(status=204, content_type="application/json")
    secure_cookie = current_app.config.get("JWT_COOKIE_SECURE", True)
    response.delete_cookie(
        "st_access_token",
        path="/",
        httponly=True,
        secure=secure_cookie,
        samesite="None" if secure_cookie else "Lax",
    )
    return response
