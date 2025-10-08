from dataclasses import dataclass

from ..exceptions import WrongUserCredentialsException
from ..models import User
from ..repositories import UserRepository

from jwt import InvalidTokenError
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
        """Authenticate the user via Smartotum.

        Args:
            email: The email address given by the user attempting to log in.
            password: The password given by the user attempting to log in.

        Returns:
            An `AuthLoginResult` containing the local user plus Smartotum access/refresh tokens.

        Raises:
            `WrongUserCredentialsException`: If the credentials are rejected or the user is unknown locally.
        """
        client = SmartotumClient()
        login_result: SmartotumLoginResult = client.login(email, password)

        try:
            claims = decode_smartotum_token(login_result.access_token)
        except InvalidTokenError as exc:
            raise WrongUserCredentialsException("Invalid Smartotum token received") from exc
        
        user_uuid = UUID(claims["sub"])

        user = UserRepository.get_user_by_uuid(user_uuid)
        
        if not user:
            raise WrongUserCredentialsException("User not registered in Privacy Dashboard!")

        return AuthLoginResult(
            user=user,
            access_token=login_result.access_token,
        )