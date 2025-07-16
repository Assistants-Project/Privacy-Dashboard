from ..models import User
from ..repositories import UserRepository


class AuthService:
    @staticmethod
    def login(email: str, password: str) -> User:
        """Checks if the provided credentials are valid to allow a user to log in.

        Args:
            email: The email address given by the user attempting to log in.
            password: The password given by the user attempting to log in.

        Returns:
            User: The authenticated user object if the credentials are valid.

        Raises:
            Exception: If the email does not correspond to any user in the
                database or the password is incorrect.
        """

        user = UserRepository.find_user_by_email(email)
        if not user or not user.check_password(password):
            raise Exception(
                "Invalid username or password"
            )  # TODO Replace with custom exception
        return user
