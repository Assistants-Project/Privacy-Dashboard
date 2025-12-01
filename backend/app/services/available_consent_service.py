from datetime import datetime
from typing import List, TypedDict
from uuid import UUID

from ..exceptions import (
    ApplicationNotFoundException,
    AvailableConsentApplicationMismatchException,
    AvailableConsentNotFoundException,
    SmartHomeNotFoundException,
    UserSmartHomeAvailableConsentAlreadyCreatedException,
    UserSmartHomeAvailableConsentCreationException,
)
from ..models import AvailableConsent
from ..repositories import (
    ApplicationRepository,
    AvailableConsentRepository,
    SmartHomeRepository,
)


class AvailableConsentGivenDict(TypedDict):
    available_consent = AvailableConsent
    application_name = str
    given_at = datetime


class AvailableConsentService:
    @staticmethod
    def get_available_consents_by_application_uuid(
        user_id: int, application_uuid: UUID
    ) -> List[AvailableConsent]:
        """Returns the list of `AvailableConsent`, if any, associated to an `Application` if the `Application` with the given `UUID`
        exists and is managed or installed by the given user.

        Args:
            user_id: The ID of the user who manages or installs the applications.
            application_uuid: The `UUID` of the `Application` to retrieve the list of `AvailableConsent` of.

        Returns:
            The list of `AvailableConsent` associated to the managed `Application` with the given `UUID`.

        Raises:
            `ApplicationNotFoundException`: If the `Application` with the given `UUID` is not found among the applications managed or installed by the given user.
        """

        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among your applications!"
            )
        return application.available_consents

    @staticmethod
    def get_given_consents_by_ds_id_and_smart_home_uuid(
        current_user_id: int, smart_home_uuid: str
    ) -> List[AvailableConsentGivenDict]:
        """Returns a list of available consents given by a `DATA_SUBJECT` user in a given `SmartHome`.

        Args:
            current_user_id: The ID of the user with role `DATA_SUBJECT` who is fetching the given consents.
            smart_home_uuid: The `UUID` of the smart home to fetch given consents of.

        Returns:
            A list of dictionaries each containing the available consent instance, the name of the application associated to the consent and the date and time it was given, or an empty list if none are found.

        Raises:
            `SmartHomeNotFoundException`: If the `SmartHome` with the given `UUID` is not found among the owned smart homes of the user.
        """

        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            current_user_id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes!"
            )
        iterator = AvailableConsentRepository.get_available_consents_by_ds_id_and_smart_home_id(
            current_user_id, smart_home.id
        )
        return [
            {
                "available_consent": available_consent,
                "application_name": application_name,
                "given_at": given_at,
            }
            for available_consent, application_name, given_at in iterator
        ]

    @staticmethod
    def give_consents_in_smart_home(
        user_id: int, smart_home_uuid: str, selected_consents_uuids: List[UUID]
    ) -> None:
        """Gives the selected consents in the given smart home owned by the given user.

        Args:
            user_id: The ID of the user who owns the smart home.
            smart_home_uuid: The `UUID` of the smart home where to give the consents.
            selected_consents_uuids: The list of `UUID` of the selected consents to give in the smart home.

        Returns:
            `None`

        Raises:
            `SmartHomeNotFoundException`: If the `SmartHome` with the given `UUID` is not found among the owned smart homes of the user.
            `AvailableConsentNotFoundException`: If one of the `AvailableConsent` with the given `UUID` in the selected consents is not found.
            `AvailableConsentApplicationMismatchException`: If the selected consents do not all belong to the same application.
            `ApplicationNotFoundException`: If the `Application` associated to the selected consents is not found among the installed applications of the given smart home.
            `UserSmartHomeAvailableConsentAlreadyCreatedException`: If one or more of the selected consents have already been given in the smart home by the user.
            `UserSmartHomeAvailableConsentCreationException`: If an error occurs while saving the selected consents in the database.
        """

        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            user_id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes!"
            )
        available_consents_ids = []
        available_consents_application_ids = []
        for consent_uuid in selected_consents_uuids:
            available_consent = (
                AvailableConsentRepository.get_available_consent_by_uuid(consent_uuid)
            )
            if not available_consent:
                raise AvailableConsentNotFoundException(
                    f"Available Consent with uuid {consent_uuid} not found!"
                )
            available_consents_ids.append(available_consent.id)
            available_consents_application_ids.append(available_consent.application_id)
        if not all(
            app_id == available_consents_application_ids[0]
            for app_id in available_consents_application_ids
        ):
            raise AvailableConsentApplicationMismatchException(
                "Selected consents do not all belong to the same application!"
            )
        if not ApplicationRepository.get_user_smart_home_application_by_ds_id_and_smart_home_id_and_application_id(
            user_id, smart_home.id, available_consents_application_ids[0]
        ):
            raise ApplicationNotFoundException(
                f"Application associated to the selected consents not found among the installed applications of smart home with uuid {smart_home_uuid}!"
            )
        for available_consent_id in available_consents_ids:
            if AvailableConsentRepository.get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
                user_id, smart_home.id, available_consent_id
            ):
                raise UserSmartHomeAvailableConsentAlreadyCreatedException(
                    "You have already given one or more of the selected consents in this smart home!"
                )
        created_consents = []
        for available_consent_id in available_consents_ids:
            try:
                created_consents.append(
                    AvailableConsentRepository.create_user_smart_home_available_consent(
                        user_id, smart_home.id, available_consent_id
                    )
                )
            except Exception:
                raise UserSmartHomeAvailableConsentCreationException(
                    "Error while saving selected consents!"
                )
        if len(created_consents) != len(selected_consents_uuids):
            raise UserSmartHomeAvailableConsentCreationException(
                "Error while saving selected consents!"
            )
        return
