from uuid import UUID

from ..exceptions import ApplicationNotFoundException
from ..models import PrivacyNotice
from ..repositories import ApplicationRepository


class PrivacyNoticeService:
    @staticmethod
    def get_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
        user_id: int, application_uuid: UUID
    ) -> PrivacyNotice | None:
        """Returns the `PrivacyNotice` associated with an `Application` if the `Application` with the given `UUID`
        exists and is managed by the given `DATA_CONTROLLER` or `DPO` user.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the applications.
            application_uuid: The UUID of the application to retrieve the privacy notice of.

        Returns:
            The `PrivacyNotice` associated with the `Application`, or `None` if not found.

        Raises:
            `ApplicationNotFoundException`: If the application with the given `UUID` is not found among the applications managed by the user.
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
        return application.privacy_notice
