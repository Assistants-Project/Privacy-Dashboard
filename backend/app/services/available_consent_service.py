from typing import List
from uuid import UUID

from ..exceptions import ApplicationNotFoundException
from ..models import AvailableConsent
from ..repositories import ApplicationRepository


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
