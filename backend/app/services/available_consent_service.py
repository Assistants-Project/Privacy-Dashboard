from datetime import datetime
from typing import List, TypedDict
from uuid import UUID

from ..exceptions import (
    ApplicationNotFoundException,
    AvailableConsentApplicationMismatchException,
    AvailableConsentNotFoundException,
    SmartHomeNotFoundException,
    UserNotFoundException,
    UserSmartHomeAvailableConsentAlreadyCreatedException,
    UserSmartHomeAvailableConsentCreationException,
    UserSmartHomeAvailableConsentDeletionException,
)
from ..models import AvailableConsent
from ..repositories import (
    ApplicationRepository,
    AvailableConsentRepository,
    SmartHomeRepository,
    UserRepository,
)


class AvailableConsentGivenDict(TypedDict):
    available_consent: AvailableConsent
    application_uuid: UUID
    given_at: datetime


class AvailableConsentService:
    @staticmethod
    def get_available_consents_by_application_uuid(
        current_user_id: int, application_uuid: UUID
    ) -> List[AvailableConsent]:
        """Returns the list of `AvailableConsent`, if any, associated to an `Application` if the `Application` with the given `UUID`
        exists and is managed or installed by the given user.

        Args:
            current_user_id: The ID of the user who manages or installs the applications.
            application_uuid: The `UUID` of the `Application` to retrieve the list of `AvailableConsent` of.

        Returns:
            The list of `AvailableConsent` associated to the managed `Application` with the given `UUID`.

        Raises:
            `ApplicationNotFoundException`: If the `Application` with the given `UUID` is not found among the applications managed or installed by the given user.
        """

        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                current_user_id, application_uuid
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
            A list of dictionaries each containing the available consent instance, the UUID of the application associated to the consent and the date and time it was given, or an empty list if none are found.

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
        given: List[AvailableConsentGivenDict] = []
        for available_consent, application_uuid, given_at in iterator:
            given.append(
                {
                    "available_consent": available_consent,
                    "application_uuid": application_uuid,
                    "given_at": given_at,
                }
            )
        return given

    @staticmethod
    def give_consents_in_smart_home(
        current_user_id: int, smart_home_uuid: str, selected_consents_uuids: List[UUID]
    ) -> None:
        """Gives the selected consents in the given smart home owned by the given user.

        Args:
            current_user_id: The ID of the user who owns the smart home.
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
            current_user_id, smart_home_uuid
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
            current_user_id, smart_home.id, available_consents_application_ids[0]
        ):
            raise ApplicationNotFoundException(
                f"Application associated to the selected consents not found among the installed applications of smart home with uuid {smart_home_uuid}!"
            )
        for available_consent_id in available_consents_ids:
            if AvailableConsentRepository.get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
                current_user_id, smart_home.id, available_consent_id
            ):
                raise UserSmartHomeAvailableConsentAlreadyCreatedException(
                    "You have already given one or more of the selected consents in this smart home!"
                )
        created_consents = []
        for available_consent_id in available_consents_ids:
            try:
                created_consents.append(
                    AvailableConsentRepository.create_user_smart_home_available_consent(
                        current_user_id, smart_home.id, available_consent_id
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

    @staticmethod
    def delete_given_consent_by_ds_uuid_and_smart_home_uuid_and_available_consent_uuid(
        current_user_id: int,
        other_user_uuid: UUID,
        smart_home_uuid: str,
        available_consent_uuid: UUID,
    ) -> None:
        """Deletes the selected given consent in the given smart home owned by the given user.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who is deleting the given consent.
            other_user_uuid: The `UUID` of the user with role `DATA_SUBJECT` who gave the consent to be deleted.
            smart_home_uuid: The `UUID` of the smart home where to delete the given consent from.
            available_consent_uuid: The `UUID` of the given consent to be deleted.

        Returns:
            `None`

        Raises:
            `UserNotFoundException`: If the `User` with the given `UUID` is not found among the contacts of the given `DATA_CONTROLLER` or `DPO` user.
            `SmartHomeNotFoundException`: If the `SmartHome` with the given `UUID` is not found among the owned smart homes of the given `DATA_SUBJECT` user.
            `AvailableConsentNotFoundException`: If the `AvailableConsent` with the given `UUID` is not found.
            `UserSmartHomeAvailableConsentDeletionException`: If an error occurs while deleting the given consent in the database.
        """

        other_user = UserRepository.get_contact_by_user_id_and_other_user_uuid(
            current_user_id, other_user_uuid
        )
        if not other_user:
            raise UserNotFoundException(
                f"User with uuid {other_user_uuid} not found among the contacts!"
            )
        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            other_user.id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes of user with uuid {other_user_uuid}!"
            )
        available_consent = AvailableConsentRepository.get_available_consent_by_uuid(
            available_consent_uuid
        )
        if not available_consent:
            raise AvailableConsentNotFoundException(
                f"Available Consent with uuid {available_consent_uuid} not found!"
            )
        try:
            AvailableConsentRepository.delete_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
                other_user.id, smart_home.id, available_consent.id
            )
        except Exception:
            raise UserSmartHomeAvailableConsentDeletionException(
                "Error while deleting the given consent!"
            )
        if AvailableConsentRepository.get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
            other_user.id, smart_home.id, available_consent.id
        ):
            raise UserSmartHomeAvailableConsentDeletionException(
                "Error while deleting the given consent!"
            )
        return

    @staticmethod
    def delete_given_consent_by_ds_uuid_and_smart_home_uuid_and_application_uuid(
        current_user_id: int,
        other_user_uuid: UUID,
        smart_home_uuid: str,
        application_uuid: UUID,
    ) -> None:
        """Deletes all given consents associated to an application in the given smart home owned by the given user.

        Args:
            current_user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who is deleting the given consents.
            other_user_uuid: The `UUID` of the user with role `DATA_SUBJECT` who gave the consents to be deleted.
            smart_home_uuid: The `UUID` of the smart home where to delete the given consents from.
            application_uuid: The `UUID` of the application associated to the given consents to be deleted.

        Returns:
            `None`

        Raises:
            `UserNotFoundException`: If the `User` with the given `UUID` is not found among the contacts of the given `DATA_CONTROLLER` or `DPO` user.
            `SmartHomeNotFoundException`: If the `SmartHome` with the given `UUID` is not found among the owned smart homes of the given `DATA_SUBJECT` user.
            `ApplicationNotFoundException`: If the `Application` with the given `UUID` is not found among the installed applications of the given smart home of the given `DATA_SUBJECT` user.
            `ApplicationNotFoundException`: If the `Application` with the given `UUID` is not found among the applications managed by the given `DATA_CONTROLLER` or `DPO` user.
            `UserSmartHomeAvailableConsentDeletionException`: If an error occurs while deleting the given consents in the database.
        """

        other_user = UserRepository.get_contact_by_user_id_and_other_user_uuid(
            current_user_id, other_user_uuid
        )
        if not other_user:
            raise UserNotFoundException(
                f"User with uuid {other_user_uuid} not found among the contacts!"
            )
        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            other_user.id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes of user with uuid {other_user_uuid}!"
            )
        user_smart_home_application = ApplicationRepository.get_user_smart_home_application_by_ds_id_and_smart_home_id_and_application_uuid(
            other_user.id, smart_home.id, application_uuid
        )
        if not user_smart_home_application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the installed applications of smart home with uuid {smart_home_uuid}!"
            )
        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                current_user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        try:
            AvailableConsentRepository.delete_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_application_id(
                other_user.id, smart_home.id, application.id
            )
        except Exception:
            raise UserSmartHomeAvailableConsentDeletionException(
                "Error while deleting the consents associated to the given application!"
            )
        if AvailableConsentRepository.get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_application_id(
            other_user.id, smart_home.id, application.id
        ):
            raise UserSmartHomeAvailableConsentDeletionException(
                "Error while deleting the consents associated to the given application!"
            )
        return
