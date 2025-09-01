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
            role: An enum that represents the role of the users to retrieve, one of `DATA_SUBJECT`, `DATA_CONTROLLER` and `DATA_PROTECTION_OFFICER`.

        Returns:
            The list of `User` instances of the given role associated with the `Application` except for the given user, or an empty list if none are found.

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

    @staticmethod
    def get_contacts_by_dc_or_dpo_id(user_id: int) -> List[User]:
        """Returns the contacts of the given user with role `DATA_CONTROLLER` or `DPO`. A contact, for
        a `DATA_CONTROLLER` or `DPO`, is any `User` of any role who has at least one managed or installed `Application`
        in common with the given `DATA_CONTROLLER` or `DPO`.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO`.

        Returns:
            The list of `User` instances that are contacts of the given user.
        """

        return UserRepository.get_contacts_by_dc_or_dpo_id(user_id)
