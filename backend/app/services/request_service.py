from typing import List, TypedDict
from uuid import UUID

from ..exceptions import ApplicationNotFoundException, UserNotFoundException
from ..models import Request
from ..repositories import ApplicationRepository, RequestRepository, UserRepository


class RequestDict(TypedDict):
    request: Request
    user_email: str
    application_name: str


class RequestService:
    @staticmethod
    def get_requests_by_dc_or_dpo_id_and_application_uuid_and_user_uuid(
        current_user_id: int, application_uuid: UUID, other_user_uuid: UUID
    ) -> List[RequestDict]:
        """Returns a list of requests fetched by an application's `UUID` and by another user's `UUID` from the database.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who is fetching requests.
            application_uuid: The `UUID` of the application to fetch requests of.
            other_user_uuid: The `UUID` of the other user who created the requests.

        Returns:
            A list of dictionaries each containing the request instance, the email of the user who created the request and the name of the application, or an empty list if none are found.

        Raises:
            `ApplicationNotFoundException`: If the application with the given `UUID` is not found among the applications managed by the given `DATA_CONTROLLER` or `DPO` user.
            `UserNotFoundException`: If the user with the given `UUID` is not found among the contacts of the given `DATA_CONTROLLER` or `DPO` user.
        """
        application = (
            ApplicationRepository.get_application_by_dc_or_dpo_id_and_application_uuid(
                current_user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        other_user = UserRepository.get_contact_by_dc_or_dpo_id_and_other_user_uuid(
            current_user_id, other_user_uuid
        )
        if not other_user:
            raise UserNotFoundException(
                f"User with uuid {other_user_uuid} not found among the contacts!"
            )
        iterator = RequestRepository.get_requests_by_application_id_and_user_id(
            application.id, other_user.id
        )
        return [
            {
                "request": request,
                "user_email": user_email,
                "application_name": application_name,
            }
            for request, user_email, application_name in iterator
        ]
