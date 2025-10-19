from flask import Response, jsonify
from flask_smorest import Blueprint

from ..schemas import AuthReqSchema, UserResSchema, RegistrationReqSchema
from ..services import AuthService
from ..utils import unlogged_required
from ..utils import logged_in_required

from flask import current_app

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
@unlogged_required()
def login(email: str, password: str):


    result = AuthService.login(email, password)

    user = result.user
    access_token = result.access_token

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


@auth_bp.route("/logout", methods=["POST"])
@auth_bp.response(204, description="Successful logout")
@logged_in_required()
def logout():
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
