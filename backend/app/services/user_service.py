from ..models import User
from ..repositories import UserRepository


class UserService:
    @staticmethod
    def get_user_by_email(email: str) -> User:
        """Returns a user fetched by its email from the database.

        Args:
            email: The email address of the user to retrieve.

        Raises:
            Exception: If no user with the given email is found in the database.
        """

        user = UserRepository.get_user_by_email(email)
        if not user:
            raise Exception("User not found")  # TODO Replace with custom exception
        return user
