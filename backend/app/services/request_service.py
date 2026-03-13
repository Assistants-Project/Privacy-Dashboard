from typing import List, NotRequired, TypedDict
from uuid import UUID

from ..exceptions import (
    ApplicationNotFoundException,
    AvailableConsentApplicationMismatchException,
    AvailableConsentEmptyListException,
    AvailableConsentNotFoundException,
    AvailableConsentWrongListException,
    MissingJWTException,
    RequestNotFoundException,
    SmartHomeNotFoundException,
    UserNotFoundException,
)
from ..models import NotificationType, Request, RightType, Status, UserRole
from ..repositories import (
    ApplicationRepository,
    ConsentRepository,
    NotificationRepository,
    ProcessingContextRepository,
    RequestRepository,
    SmartHomeRepository,
    UserRepository,
)
from ..extensions import db
from ..services.consent_policy_rule_service import ConsentPolicyRuleService
from ..services.dht_service import DHTService
from config import BaseConfig


class RequestDict(TypedDict):
    request: Request
    user_email: str
    user_firstname: str | None
    user_lastname: str | None
    application_name: str
    application_uuid: UUID
    processing_context_uuid: UUID

class RequestSubmitPayload(TypedDict):
    right_type: RightType
    additional_information: str
    smart_home_uuid: str
    application_uuid: UUID
    selected_consents: NotRequired[list[UUID] | None]


class SelectedConsentSnapshot(TypedDict):
    uuid: str
    content: str | None


class RequestService:
    @staticmethod
    def _build_request_notification_payload(request: Request) -> dict[str, str]:
        return {
            "right_type": request.right_type.value,
        }

    @staticmethod
    def _get_request_submitted_receiver_ids(application_id: int) -> list[int]:
        return list(
            {
                recipient.id
                for recipient in UserRepository.get_users_by_application_id_and_user_role(
                    application_id, UserRole.DATA_CONTROLLER
                )
            }
            | {
                recipient.id
                for recipient in UserRepository.get_users_by_application_id_and_user_role(
                    application_id, UserRole.DATA_PROTECTION_OFFICER
                )
            }
        )

    @staticmethod
    def _create_request_submitted_notification(
        request: Request,
        sender_id: int,
        sender_email: str,
        receiver_ids: list[int],
        application_id: int,
        processing_context_id: int,
    ) -> None:
        if not receiver_ids:
            return
        NotificationRepository.create_notification(
            NotificationType.REQUEST_SUBMITTED,
            sender_id,
            sender_email,
            receiver_ids,
            application_id=application_id,
            request_id=request.id,
            processing_context_id=processing_context_id,
            payload=RequestService._build_request_notification_payload(request),
            commit=False,
        )

    @staticmethod
    def _get_request_handled_notification_type(
        previous_status: Status,
        previous_response: str | None,
        next_status: Status,
        next_response: str | None,
    ) -> NotificationType | None:
        previous_response_normalized = (previous_response or "").strip()
        next_response_normalized = (next_response or "").strip()

        if next_response_normalized and next_response_normalized != previous_response_normalized:
            return NotificationType.REQUEST_ANSWERED
        if previous_status != next_status:
            return NotificationType.REQUEST_STATUS_UPDATED
        return None

    @staticmethod
    def _create_request_handled_notification(
        request: Request,
        sender_id: int,
        sender_email: str,
        receiver_ids: list[int],
        application_id: int,
        processing_context_id: int,
        notification_type: NotificationType | None,
    ) -> None:
        if not receiver_ids or notification_type is None:
            return
        NotificationRepository.create_notification(
            notification_type,
            sender_id,
            sender_email,
            receiver_ids,
            application_id=application_id,
            request_id=request.id,
            processing_context_id=processing_context_id,
            payload=RequestService._build_request_notification_payload(request),
            commit=False,
        )

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
                "user_firstname": user_firstname,
                "user_lastname": user_lastname,
                "application_name": application_name,
                "application_uuid": application_uuid,
                "processing_context_uuid": processing_context_uuid,
            }
            for request, user_email, user_firstname, user_lastname, application_name, application_uuid, processing_context_uuid in iterator
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
                "user_firstname": user_firstname,
                "user_lastname": user_lastname,
                "application_name": application_name,
                "application_uuid": application_uuid,
                "processing_context_uuid": processing_context_uuid,
            }
            for request, user_email, user_firstname, user_lastname, application_name, application_uuid, processing_context_uuid in iterator
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
        iterator = RequestRepository.get_requests_by_ds_id_and_smart_home_uuid_and_status(
            current_user_id, smart_home.uuid, status
        )
        return [
            {
                "request": request,
                "user_email": user_email,
                "user_firstname": user_firstname,
                "user_lastname": user_lastname,
                "application_name": application_name,
                "application_uuid": application_uuid,
                "processing_context_uuid": processing_context_uuid,
            }
            for request, user_email, user_firstname, user_lastname, application_name, application_uuid, processing_context_uuid in iterator
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
        user = UserRepository.get_user_by_id(current_user_id)
        if not user:
            raise UserNotFoundException("User not found")
        application = user_smart_home_application.application
        processing_context = ProcessingContextRepository.get_or_create_processing_context(
            current_user_id,
            user.email,
            user_smart_home_application.application_id,
            application.uuid,
            application.name,
            smart_home.uuid,
            user_smart_home_application.id,
        )
        receiver_ids = RequestService._get_request_submitted_receiver_ids(
            user_smart_home_application.application_id
        )

        selected_consents = None
        if request["right_type"] == RightType.WITHDRAW_CONSENT:
            selected_consents, selected_consent_uuids, available_consent_ids, action_ids_by_uuid = (
                RequestService._validate_selected_consents_for_withdraw_request(
                    current_user_id,
                    smart_home.id,
                    user_smart_home_application.application_id,
                    request.get("selected_consents"),
                )
            )
            consent_uuids_with_action = [
                consent_uuid
                for consent_uuid in selected_consent_uuids
                if action_ids_by_uuid.get(consent_uuid)
            ]
            access_token: str | None = None
            cps: ConsentPolicyRuleService | None = None
            dht: DHTService | None = None
            published_dht_uuids: list[str] = []

            try:
                # A withdraw request is valid even without Smartotum action mappings:
                # only consents linked to a SIFIS action produce an automatic deny policy.
                if consent_uuids_with_action:
                    from flask import request as flask_request

                    access_token = flask_request.cookies.get("st_access_token")
                    if not access_token:
                        raise MissingJWTException("Smartotum access token missing")

                    cps = ConsentPolicyRuleService()
                    dht = DHTService(BaseConfig.SMARTOTUM_DHT_URL, BaseConfig.SMARTOTUM_RULE_TOPIC)

                for consent_uuid in consent_uuids_with_action:
                    action_id = action_ids_by_uuid[consent_uuid]
                    _db_rule_id, published = cps.create_consent_deny_rule(
                        smart_home=smart_home,
                        subject_email=user.email,
                        consent_uuid=consent_uuid,
                        sifis_action_id=action_id,
                        access_token=access_token,
                    )
                    published_dht_uuids.extend(published)

                unique_available_consent_ids = list(set(available_consent_ids))
                ConsentRepository.delete_user_smart_home_available_consents_by_ds_id_and_smart_home_id_and_available_consent_ids(
                    current_user_id, smart_home.id, unique_available_consent_ids
                )

                created = RequestRepository.create_request(
                    request["right_type"],
                    request["additional_information"],
                    user_smart_home_application.id,
                    data_subject_user_id=current_user_id,
                    application_id=user_smart_home_application.application_id,
                    smart_home_uuid=smart_home.uuid,
                    processing_context_id=processing_context.id,
                    selected_consents=selected_consents,
                    commit=False,
                )
                RequestService._create_request_submitted_notification(
                    created,
                    current_user_id,
                    user.email,
                    receiver_ids,
                    user_smart_home_application.application_id,
                    processing_context.id,
                )
                db.session.commit()
                return created
            except Exception:
                db.session.rollback()
                # Best-effort cleanup of published DHT entries
                for dht_uuid in published_dht_uuids:
                    try:
                        if dht and access_token:
                            dht.delete_rule_strict(
                                rule_uuid=str(dht_uuid),
                                home_uuid=str(smart_home.uuid),
                                access_token=access_token,
                            )
                    except Exception:
                        pass
                raise

        created = RequestRepository.create_request(
            request["right_type"],
            request["additional_information"],
            user_smart_home_application.id,
            data_subject_user_id=current_user_id,
            application_id=user_smart_home_application.application_id,
            smart_home_uuid=smart_home.uuid,
            processing_context_id=processing_context.id,
            selected_consents=selected_consents,
            commit=False,
        )
        RequestService._create_request_submitted_notification(
            created,
            current_user_id,
            user.email,
            receiver_ids,
            user_smart_home_application.application_id,
            processing_context.id,
        )
        db.session.commit()
        return created
    
    #valida i consensi essendo scritti in testo
    #controlla che il consenso esista
    #controlla che il consenso appartenga all'app da cui provinee la richiesta
    #controlla che il consenso sia stato dato
    # se tutto ok lo ritorna a submit_request che lo considera validato
    @staticmethod
    def _validate_selected_consents_for_withdraw_request(
        current_user_id: int,
        smart_home_id: int,
        application_id: int,
        selected_consents_uuids: list[UUID] | None,
    ) -> tuple[
        list[SelectedConsentSnapshot],
        list[UUID],
        list[int],
        dict[UUID, str | None],
    ]:
        
        #nessun consenso
        if not selected_consents_uuids:
            raise AvailableConsentEmptyListException("No consents selected!")
        
        #consensi duplicati
        if len(selected_consents_uuids) != len(set(selected_consents_uuids)):
            raise AvailableConsentWrongListException("Duplicate consents selected!")

        selected_consents: list[SelectedConsentSnapshot] = []
        selected_consent_uuids: list[UUID] = []
        available_consent_ids: list[int] = []
        action_ids_by_uuid: dict[UUID, str | None] = {}

        for consent_uuid in selected_consents_uuids:

            available_consent = ConsentRepository.get_available_consent_by_uuid(consent_uuid)

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
            given_consent = ConsentRepository.get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
                current_user_id, smart_home_id, available_consent.id
            )
            if not given_consent:
                raise AvailableConsentNotFoundException(
                    f"Available Consent with uuid {consent_uuid} is not currently given in this smart home!"
                )
            selected_consents.append(
                {
                    "uuid": str(available_consent.uuid),
                    "content": available_consent.content,
                }
            )
            selected_consent_uuids.append(consent_uuid)
            available_consent_ids.append(available_consent.id)
            action_ids_by_uuid[consent_uuid] = getattr(available_consent, "sifis_action_id", None)

        return selected_consents, selected_consent_uuids, available_consent_ids, action_ids_by_uuid

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
        current_user = UserRepository.get_user_by_id(current_user_id)
        if not current_user:
            raise UserNotFoundException("User not found")

        notification_type = RequestService._get_request_handled_notification_type(
            request.status,
            request.response,
            status,
            response,
        )

        updated_request = RequestRepository.update_request_status_and_response(
            request.id, response, status, commit=False
        )
        RequestService._create_request_handled_notification(
            updated_request,
            current_user_id,
            current_user.email,
            [updated_request.data_subject_user_id],
            updated_request.application_id,
            updated_request.processing_context_id,
            notification_type,
        )
        db.session.commit()
        return updated_request
