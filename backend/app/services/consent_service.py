from datetime import datetime
from typing import List, TypedDict
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..exceptions import (
    ApplicationNotFoundException,
    ApplicationNotManagedException,
    AvailableConsentApplicationMismatchException,
    AvailableConsentEmptyListException,
    AvailableConsentNotFoundException,
    AvailableConsentWrongListException,
    MissingJWTException,
    SmartHomeNotFoundException,
    UserNotFoundException,
)
from ..models import AvailableConsent, NotificationType, UserRole
from ..repositories import (
    ApplicationRepository,
    ConsentRepository,
    NotificationRepository,
    ProcessingContextRepository,
    SmartHomeRepository,
    UserRepository,
)
from ..services.consent_policy_rule_service import ConsentPolicyRuleService


class ConsentStateDict(TypedDict):
    uuid: UUID
    content: str
    given: bool
    given_at: datetime | None
    sifis_action_id: str | None


def normalize_available_consents_payload(available_consents: list[str] | None, *, deduplicate: bool) -> list[str]:
    normalized_available_consents: list[str] = []
    if available_consents is not None:
        for available_consent in available_consents:
            if not isinstance(available_consent, str):
                raise AvailableConsentWrongListException(
                    "Available consents must be a list of non-empty strings!"
                )
            normalized_available_consent = available_consent.strip()
            if not normalized_available_consent:
                raise AvailableConsentWrongListException(
                    "Available consents must be a list of non-empty strings!"
                )
            normalized_available_consents.append(normalized_available_consent)

    if deduplicate:
        return list(dict.fromkeys(normalized_available_consents))

    if len(normalized_available_consents) != len(set(normalized_available_consents)):
        raise AvailableConsentWrongListException("Duplicate consents selected!")

    return normalized_available_consents


class ConsentService:
    @staticmethod
    def _is_smartotum_application_name(application_name: str) -> bool:
        return "com.smartotum" in (application_name or "").lower()

    @staticmethod
    def add_available_consent_to_managed_application(
        current_user_id: int, application_uuid: UUID, content: str
    ) -> AvailableConsent:
        """Creates a new available consent for a managed application.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who is creating the consent.
            application_uuid: The `UUID` of the managed application where the consent is added.
            content: The textual content of the consent to add.

        Returns:
            The created `AvailableConsent` instance.

        Raises:
            `ApplicationNotFoundException`: If the application with the given `UUID` is not found among managed applications.
            `AvailableConsentWrongListException`: If the content is blank or already exists for the application.
        """
        application = ApplicationRepository.get_application_by_user_id_and_application_uuid(
            current_user_id, application_uuid
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among your managed applications!"
            )
        if ConsentService._is_smartotum_application_name(application.name):
            raise ApplicationNotManagedException(
                "Consents for Smartotum applications are managed by Smartotum and cannot be edited in the Privacy Dashboard."
            )

        normalized_content = content.strip()
        if not normalized_content:
            raise AvailableConsentWrongListException("Consent content cannot be blank!")
        try:
            available_consent = ConsentRepository.create_available_consent(
                application.id, normalized_content
            )
            db.session.commit()
            return available_consent
        except IntegrityError:
            db.session.rollback()
            raise AvailableConsentWrongListException(
                "Consent already exists for this application!"
            )

    @staticmethod
    def remove_available_consent_from_managed_application(
        current_user_id: int, application_uuid: UUID, available_consent_uuid: UUID
    ) -> None:
        """Deletes an available consent from a managed application.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who is deleting the consent.
            application_uuid: The `UUID` of the managed application where the consent is removed.
            available_consent_uuid: The `UUID` of the available consent to delete.

        Returns:
            `None`.

        Raises:
            `ApplicationNotFoundException`: If the application with the given `UUID` is not found among managed applications.
            `AvailableConsentNotFoundException`: If the available consent with the given `UUID` is not found for the application.
        """
        application = ApplicationRepository.get_application_by_user_id_and_application_uuid(
            current_user_id, application_uuid
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among your managed applications!"
            )
        if ConsentService._is_smartotum_application_name(application.name):
            raise ApplicationNotManagedException(
                "Consents for Smartotum applications are managed by Smartotum and cannot be edited in the Privacy Dashboard."
            )

        deleted = (
            ConsentRepository.delete_available_consent_by_application_id_and_uuid(
                application.id, available_consent_uuid
            )
        )
        if not deleted:
            raise AvailableConsentNotFoundException(
                f"Available Consent with uuid {available_consent_uuid} not found for application {application_uuid}!"
            )
        db.session.commit()
        return

    @staticmethod
    def get_available_consents_by_application_uuid(
        current_user_id: int, application_uuid: UUID
    ) -> List[AvailableConsent]:
        """Returns all available consents for a visible application.

        Args:
            current_user_id: The ID of the logged user requesting the list.
            application_uuid: The `UUID` of the application whose available consents are requested.

        Returns:
            A list of `AvailableConsent` instances, or an empty list if none are configured.

        Raises:
            `ApplicationNotFoundException`: If the application with the given `UUID` is not visible to the current user.
        """
        application = ApplicationRepository.get_application_by_user_id_and_application_uuid(
            current_user_id, application_uuid
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among your applications!"
            )
        return application.available_consents

    
    @staticmethod
    def get_consents_state_by_ds_id_and_smart_home_uuid_and_application_uuid(
        current_user_id: int, smart_home_uuid: str, application_uuid: UUID
    ) -> List[ConsentStateDict]:
        """Returns available consents for an app with their given/not-given state in a smart home.

        Args:
            current_user_id: The ID of the user with role `DATA_SUBJECT` who is fetching consent state.
            smart_home_uuid: The `UUID` of the smart home where consent state is evaluated.
            application_uuid: The `UUID` of the installed application in that smart home.

        Returns:
            A list of dictionaries containing consent `uuid`, `content`, `given` and `given_at`.

        Raises:
            `SmartHomeNotFoundException`: If the smart home with the given `UUID` is not found among owned homes.
            `ApplicationNotFoundException`: If the application with the given `UUID` is not installed in the smart home.
        """
        smart_home_id, application_id = (
            ConsentService._get_installed_application_ids_for_ds_in_home(
                current_user_id, smart_home_uuid, application_uuid
            )
        )
        iterator = ConsentRepository.get_available_consents_with_given_state_by_ds_id_and_smart_home_id_and_application_id(
            current_user_id, smart_home_id, application_id
        )
        return [
            {
                "uuid": available_consent.uuid,
                "content": available_consent.content,
                "given": given_at is not None,
                "given_at": given_at,
                "sifis_action_id": getattr(available_consent, "sifis_action_id", None),
            }
            for available_consent, given_at in iterator
        ]

    @staticmethod
    def set_given_consents_by_ds_id_and_smart_home_uuid_and_application_uuid(
        current_user_id: int,
        smart_home_uuid: str,
        application_uuid: UUID,
        selected_consents_uuids: List[UUID],
    ) -> None:
        """Marks selected consents as given for a DS in a specific smart home and application.
        Makes sure that the rules has been succeffully deleted before setting the consent as given

        Args:
            current_user_id: The ID of the user with role `DATA_SUBJECT` who is giving consents.
            smart_home_uuid: The `UUID` of the smart home where consents are given.
            application_uuid: The `UUID` of the installed application for the selected consents.
            selected_consents_uuids: The list of consent `UUID`s to set as given.

        Returns:
            `None`.

        Raises:
            `AvailableConsentEmptyListException`: If no consents are selected.
            `AvailableConsentWrongListException`: If duplicate consent UUIDs are selected.
            `SmartHomeNotFoundException`: If the smart home with the given `UUID` is not found among owned homes.
            `ApplicationNotFoundException`: If the application with the given `UUID` is not installed in the smart home.
            `AvailableConsentNotFoundException`: If a selected consent does not exist.
            `AvailableConsentApplicationMismatchException`: If selected consents do not belong to the requested application.
        """
        if not selected_consents_uuids:
            raise AvailableConsentEmptyListException("No consents selected!")
        if len(selected_consents_uuids) != len(set(selected_consents_uuids)):
            raise AvailableConsentWrongListException("Duplicate consents selected!")

        smart_home_id, application_id = (
            ConsentService._get_installed_application_ids_for_ds_in_home(
                current_user_id, smart_home_uuid, application_uuid
            )
        )

        available_consents_ids: list[int] = []
        available_consents_by_id: dict[int, AvailableConsent] = {}
        action_ids_by_uuid: dict[UUID, str | None] = {}
        for consent_uuid in selected_consents_uuids:
            available_consent = ConsentRepository.get_available_consent_by_uuid(
                consent_uuid
            )
            if not available_consent:
                raise AvailableConsentNotFoundException(
                    f"Available Consent with uuid {consent_uuid} not found!"
                )
            if available_consent.application_id != application_id:
                raise AvailableConsentApplicationMismatchException(
                    "Selected consents do not all belong to the requested application!"
                )
            available_consents_ids.append(available_consent.id)
            available_consents_by_id[available_consent.id] = available_consent
            action_ids_by_uuid[consent_uuid] = getattr(available_consent, "sifis_action_id", None)

        from flask import request as flask_request
        access_token = flask_request.cookies.get("st_access_token")
        if not access_token:
            raise MissingJWTException("Smartotum access token missing")

        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            current_user_id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes!"
            )
        user = UserRepository.get_user_by_id(current_user_id)
        if not user:
            raise UserNotFoundException("User not found")
        application = ApplicationRepository.get_application_by_uuid(application_uuid)
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the installed applications of smart home with uuid {smart_home_uuid}!"
            )
        user_smart_home_application = ApplicationRepository.get_user_smart_home_application_by_ds_id_and_smart_home_id_and_application_id(
            current_user_id, smart_home.id, application_id
        )
        processing_context = ProcessingContextRepository.get_or_create_processing_context(
            current_user_id,
            user.email,
            application.id,
            application.uuid,
            application.name,
            smart_home.uuid,
            user_smart_home_application.id if user_smart_home_application else None,
        )

        cps = ConsentPolicyRuleService()
        try:
            # Delete consent-related rules first. If this fails, do not mark consents as given.
            for consent_uuid, action_id in action_ids_by_uuid.items():
                # Not every consent is mapped to an automatic deny rule.
                # If there's no mapping, we can still accept the consent.
                if not action_id:
                    continue
                cps.delete_consent_deny_rule(
                    smart_home=smart_home,
                    consent_uuid=consent_uuid,
                    sifis_action_id=action_id,
                    access_token=access_token,
                )

            newly_granted_consents: list[AvailableConsent] = []
            for available_consent_id in available_consents_ids:
                created = ConsentRepository.ensure_user_smart_home_available_consent(
                    current_user_id, smart_home_id, available_consent_id
                )
                if created:
                    newly_granted_consents.append(available_consents_by_id[available_consent_id])

            receiver_ids = list(
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
            for granted_consent in newly_granted_consents:
                if not receiver_ids:
                    break
                NotificationRepository.create_notification(
                    NotificationType.CONSENT_GRANTED,
                    current_user_id,
                    user.email,
                    receiver_ids,
                    application_id=application_id,
                    processing_context_id=processing_context.id,
                    payload={
                        "consent_uuid": str(granted_consent.uuid),
                        "consent_content": granted_consent.content,
                    },
                    commit=False,
                )
            db.session.commit()
            return
        except Exception:
            db.session.rollback()
            raise


    @staticmethod
    def _get_installed_application_ids_for_ds_in_home(
        current_user_id: int, smart_home_uuid: str, application_uuid: UUID
    ) -> tuple[int, int]:
        """Resolves internal smart home and application IDs for a DS-scoped installed app.

        Args:
            current_user_id: The ID of the user with role `DATA_SUBJECT`.
            smart_home_uuid: The `UUID` of the smart home owned by the user.
            application_uuid: The `UUID` of the application installed in that smart home.

        Returns:
            A tuple `(smart_home_id, application_id)` with internal DB IDs.

        Raises:
            `SmartHomeNotFoundException`: If the smart home with the given `UUID` is not found among owned homes.
            `ApplicationNotFoundException`: If the application with the given `UUID` is not installed in the specified smart home.
        """
        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            current_user_id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes!"
            )

        user_smart_home_application = ApplicationRepository.get_user_smart_home_application_by_ds_id_and_smart_home_id_and_application_uuid(
            current_user_id, smart_home.id, application_uuid
        )
        if not user_smart_home_application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the installed applications of smart home with uuid {smart_home_uuid}!"
            )

        return smart_home.id, user_smart_home_application.application_id
