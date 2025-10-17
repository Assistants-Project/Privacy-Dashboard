from dataclasses import dataclass

from ..exceptions import WrongUserCredentialsException
from ..models import User, UserRole
from ..repositories import UserRepository

from jwt import InvalidTokenError
from flask_jwt_extended import (
    create_access_token,
)
from uuid import UUID
from ..integrations.smartotum import decode_smartotum_token
from ..integrations.smartotum import SmartotumClient, SmartotumLoginResult


@dataclass
class AuthLoginResult:
    user: User
    access_token: str


class AuthService:
    @staticmethod
    def login(email: str, password: str) -> AuthLoginResult:

        """
        Checks is the user is a DPO or Data Controller, if it is, it checks if the provided credentials are valid to allow a user to log in.
        If the user is a data subject it delegates the login to Smartotum

        Args:
            email: The email address given by the user attempting to log in.
            password: The password given by the user attempting to log in.

        Returns:
            An `AuthLoginResult` containing the local user plus Smartotum access/refresh tokens.

        Raises:
            `WrongUserCredentialsException`: If the email does not correspond to any user in the
                database or the password is incorrect.
        """

        user = UserRepository.get_user_by_email(email)
        if not user:
            raise  WrongUserCredentialsException("Invalid email or password!")
        if user.role != UserRole.DATA_SUBJECT:
            if not user.check_password(password):
                raise WrongUserCredentialsException("Invalid email or password!")
            else:
                access_token = create_access_token(identity=user.uuid, additional_claims={"role": user.role.value})
                return AuthLoginResult(user=user,access_token=access_token)

        # if we are here the user is a Data Subject
        client = SmartotumClient()
        login_result: SmartotumLoginResult = client.login(email, password)

        try:
            claims = decode_smartotum_token(login_result.access_token)
        except InvalidTokenError as exc:
            raise WrongUserCredentialsException("Invalid Smartotum token received") from exc
        
        user_uuid = UUID(claims["sub"])

        user = UserRepository.get_user_by_uuid(user_uuid)
        
        if not user:
            raise WrongUserCredentialsException("Invalid email or password!")

        return AuthLoginResult(
            user=user,
            access_token=login_result.access_token,
        )
