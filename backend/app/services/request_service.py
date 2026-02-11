from typing import List, NotRequired, TypedDict
from uuid import UUID

from ..exceptions import (
    ApplicationNotFoundException,
    AvailableConsentApplicationMismatchException,
    AvailableConsentEmptyListException,
    AvailableConsentNotFoundException,
    AvailableConsentWrongListException,
    RequestNotFoundException,
    SmartHomeNotFoundException,
    UserNotFoundException,
)
from ..models import Request, RightType, Status
from ..repositories import (
    ApplicationRepository,
    AvailableConsentRepository,
    RequestRepository,
    SmartHomeRepository,
    UserRepository,
)


class RequestDict(TypedDict):
    request: Request
    user_email: str
    application_name: str
    application_uuid: UUID

class RequestSubmitPayload(TypedDict):
    right_type: RightType
    additional_information: str
    smart_home_uuid: str
    application_uuid: UUID
    selected_consents: NotRequired[list[UUID] | None]


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
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                current_user_id, application_uuid
            )
        )
        # applicazione deve essere tra quelle gestite dal data controller
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
                "application_uuid": application_uuid,
            }
            for request, user_email, application_name, application_uuid in iterator
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
                "application_uuid": application_uuid,
            }
            for request, user_email, application_name, application_uuid in iterator
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
            # la casa deve essere del data subject
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
                "application_uuid": application_uuid,
            }
            for request, user_email, application_name, application_uuid in iterator
        ]

    @staticmethod
    def submit_request(current_user_id: int, request: RequestSubmitPayload) -> Request:
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

        selected_consents = None
        if request["right_type"] == RightType.WITHDRAW_CONSENT:
            selected_consents = (
                RequestService._validate_selected_consents_for_withdraw_request(
                    current_user_id,
                    smart_home.id,
                    user_smart_home_application.application_id,
                    request.get("selected_consents"),
                )
            )

        return RequestRepository.create_request(
            request["right_type"],
            request["additional_information"],
            user_smart_home_application.id,
            selected_consents,
        )
    
    #valida i consensi essendo scritti in testo
    #controlla che il consenso esista
    #controlla che il consenso appartenga all'app da cui provinee la richiesta
    #controlla che il consenso sia stato dato
    # se tutto ok lo ritorna a submit_request che lo considera validato
    @staticmethod
    def _validate_selected_consents_for_withdraw_request(current_user_id: int,smart_home_id: int,application_id: int,selected_consents_uuids: list[UUID] | None,) -> list[UUID]:
        
        #nessun consenso
        if not selected_consents_uuids:
            raise AvailableConsentEmptyListException("No consents selected!")
        
        #consensi duplicati
        if len(selected_consents_uuids) != len(set(selected_consents_uuids)):
            raise AvailableConsentWrongListException("Duplicate consents selected!")

        selected_consents: list[UUID] = []

        for consent_uuid in selected_consents_uuids:

            available_consent = AvailableConsentRepository.get_available_consent_by_uuid(consent_uuid)

            if not available_consent:
                raise AvailableConsentNotFoundException(
                    f"Available Consent with uuid {consent_uuid} not found!"
                )
            
            #controllare per ciascun uuid a che applicazione appartiene
            #deve appartenere alla stessa applicazione a cui è stato dato
            if available_consent.application_id != application_id:
                raise AvailableConsentApplicationMismatchException(
                    "Selected consents do not all belong to the requested application!"
                )
            given_consent = AvailableConsentRepository.get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
                current_user_id, smart_home_id, available_consent.id
            )
            if not given_consent:
                raise AvailableConsentNotFoundException(
                    f"Available Consent with uuid {consent_uuid} is not currently given in this smart home!"
                )
            selected_consents.append(consent_uuid)

        return selected_consents

    @staticmethod
    def handle_request(
        current_user_id: int, request_uuid: UUID, response: str | None, status: Status
    ) -> Request:
        """Handles a request for a given application in a given smart home for a given user by adding a response and changing the status.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who is handling the request.
            request_uuid: The `UUID` of the request to be handled.
            request_handling: An object containing the response and the status of the request to update.

        Returns:
            The handled `Request` for a given application in a given smart home for a given user.

        Raises:
            `RequestNotFoundException`: If the `Request` with the given `UUID` is not found among the requests of the managed applications.
        """

        request = RequestRepository.get_request_by_dc_or_dpo_id_and_request_uuid(
            current_user_id, request_uuid
        )
        if not request:
            raise RequestNotFoundException(
                f"Request with uuid {request_uuid} not found among the requests of the managed applications!"
            )
        
        #se la richiesta è di tipo Withdraw_Consent e il data controller la mette come gestita
        if (status == Status.HANDLED and request.right_type == RightType.WITHDRAW_CONSENT):

            #chiama il metodo che si occupa di fare withdraw della richiesta
            RequestService._withdraw_selected_consents_for_request(request)

        #aggiorna la richiesta e ritorna quella aggiornata
        return RequestRepository.update_request_status_and_response(request.id, response, status)

    #permette di revocare i consensi nella richiesta
    @staticmethod
    def _withdraw_selected_consents_for_request(request: Request) -> None:

        relation = request.user_smart_home_application_relation
        if relation.smart_home_id is None or not request.selected_consents:
            return

        available_consent_ids: list[int] = []
        for consent_uuid in request.selected_consents:

            available_consent = AvailableConsentRepository.get_available_consent_by_uuid(consent_uuid)
            
            if not available_consent:
                continue
            
            if available_consent.application_id != relation.application_id:
                continue
            
            available_consent_ids.append(available_consent.id)

        unique_available_consent_ids = list(set(available_consent_ids))

        AvailableConsentRepository.delete_user_smart_home_available_consents_by_ds_id_and_smart_home_id_and_available_consent_ids(
            relation.user_id, relation.smart_home_id, unique_available_consent_ids
        )
        return
