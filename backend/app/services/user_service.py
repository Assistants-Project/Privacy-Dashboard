from typing import List
from uuid import UUID

from ..exceptions import ApplicationNotFoundException, UserNotFoundException
from ..models import User, UserRole
from ..repositories import ApplicationRepository, UserRepository


class UserService:
    @staticmethod
    def get_user_by_email(email: str) -> User:
        """Returns a user fetched by its email from the database.

        Args:
            email: The email address of the user to retrieve.

        Raises:
            `UserNotFoundException`: If no user with the given email is found in the database.
        """

        user = UserRepository.get_user_by_email(email)
        if not user:
            raise UserNotFoundException(f"User with email {email} not found")
        return user

    @staticmethod
    def get_users_by_dc_or_dpo_id_and_application_uuid_and_user_role(
        user_id: int, application_uuid: UUID, role: UserRole
    ) -> List[User]:
        """Returns the users of the given role associated with an `Application` if the `Application` with the given `UUID`
        exists and is managed by the given `DATA_CONTROLLER` or `DPO` user.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the applications.
            application_uuid: The UUID of the application to retrieve the users of.
            role: An enum that represents the role of the user, one of `DATA_SUBJECT`, `DATA_CONTROLLER` and `DATA_PROTECTION_OFFICER`.

        Returns:
            The the list of `User` instances of the given role associated with the `Application` except for the given user, or an empty list if none are found.

        Raises:
            `ApplicationNotFoundException`: If the application with the given `UUID` is not found among the applications managed by the  user.
        """

        application = (
            ApplicationRepository.get_application_by_dc_or_dpo_id_and_application_uuid(
                user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        users = UserRepository.get_users_by_application_id_and_user_role(
            application.id, role
        )
        return [user for user in users if user.id != user_id]
