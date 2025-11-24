from typing import List, TypedDict
from uuid import UUID

from ..exceptions import (
    ApplicationNotFoundException,
    SmartHomeNotFoundException,
    UserNotFoundException,
)
from ..models import Request, Status
from ..repositories import (
    ApplicationRepository,
    RequestRepository,
    SmartHomeRepository,
    UserRepository,
)
from ..schemas import RequestReqSchema


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
        other_user = UserRepository.get_contact_by_user_id_and_other_user_uuid(
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

    @staticmethod
    def get_requests_by_dc_or_dpo_id(
        current_user_id: int, status: Status | None
    ) -> List[RequestDict]:
        """Returns a list of requests fetched by a `DATA_CONTROLLER` or `DPO` user's ID and filtered by status from the database.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who is fetching requests.
            status: The optional status to filter requests by.

        Returns:
            A list of dictionaries each containing the request instance, the email of the user who created the request and the name of the application, or an empty list if none are found.
        """

        iterator = RequestRepository.get_requests_by_dc_or_dpo_id_and_status(
            current_user_id, status
        )
        return [
            {
                "request": request,
                "user_email": user_email,
                "application_name": application_name,
            }
            for request, user_email, application_name in iterator
        ]

    @staticmethod
    def get_requests_by_ds_id_and_smart_home_uuid(
        current_user_id: int, smart_home_uuid: str, status: Status | None
    ) -> List[RequestDict]:
        """Returns a list of requests fetched by a smart home's `UUID` and filtered by status from the database.

        Args:
            current_user_id: The ID of the user with role `DATA_SUBJECT` who is fetching requests.
            smart_home_uuid: The `UUID` of the smart home to fetch requests of.
            status: The optional status to filter requests by.

        Returns:
            A list of dictionaries each containing the request instance, the email of the user who created the request and the name of the application, or an empty list if none are found.

        Raises:
            `SmartHomeNotFoundException`: If the `SmartHome` with the given `UUID` is not found among the owned smart homes.
        """

        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            current_user_id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes!"
            )
        iterator = RequestRepository.get_requests_by_ds_id_and_smart_home_id_and_status(
            current_user_id, smart_home.id, status
        )
        return [
            {
                "request": request,
                "user_email": user_email,
                "application_name": application_name,
            }
            for request, user_email, application_name in iterator
        ]

    @staticmethod
    def submit_request(current_user_id: int, request: RequestReqSchema) -> Request:
        """Submits a request for a given application in a given smart home for a given user.

        Args:
            current_user_id: The ID of the user with role `DATA_SUBJECT` who submits the request.
            request: An object containing the right type, the additional information, the `UUID` of the smart home and the `UUID` of the application.

        Returns:
            The submitted `Request` for a given application in a given smart home for a given user.

        Raises:
            `SmartHomeNotFoundException`: If the `SmartHome` with the given `UUID` is not found among the owned smart homes.
            `ApplicationNotFoundException`: If the `Application` with the given `UUID` is not found among the installed applications of the given smart home.
        """

        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            current_user_id, request["smart_home_uuid"]
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {request['smart_home_uuid']} not found among the owned smart homes!"
            )
        user_smart_home_application = ApplicationRepository.get_user_smart_home_application_by_ds_id_and_smart_home_id_and_application_uuid(
            current_user_id, smart_home.id, request["application_uuid"]
        )
        if not user_smart_home_application:
            raise ApplicationNotFoundException(
                f"Application with uuid {request['application_uuid']} not found among the installed applications of smart home with uuid {request['smart_home_uuid']}!"
            )
        return RequestRepository.create_request(
            request["right_type"],
            request["additional_information"],
            user_smart_home_application.id,
        )
