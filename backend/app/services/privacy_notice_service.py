from uuid import UUID

from ..exceptions import (
    ApplicationNotFoundException,
    PrivacyNoticeAlreadyExists,
    PrivacyNoticeNotFoundException,
)
from ..models import PrivacyNotice
from ..repositories import ApplicationRepository, PrivacyNoticeRepository


class PrivacyNoticeService:
    @staticmethod
    def get_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
        user_id: int, application_uuid: UUID
    ) -> PrivacyNotice:
        """Returns the `PrivacyNotice`, if any, associated to an `Application` if the `Application` with the given `UUID`
        exists and is managed by the given `DATA_CONTROLLER` or `DPO` user.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the applications.
            application_uuid: The `UUID` of the `Application` to retrieve the `PrivacyNotice` of.

        Returns:
            The `PrivacyNotice` associated to the managed `Application` with the given `UUID`.

        Raises:
            `ApplicationNotFoundException`: If the `Application` with the given `UUID` is not found among the applications managed by the given `DATA_CONTROLLER` or `DPO` user.
            `PrivacyNoticeNotFoundException`: If no `PrivacyNotice` is found for the managed `Application` with the given `UUID`.
        """

        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        privacy_notice = application.privacy_notice
        if not privacy_notice:
            raise PrivacyNoticeNotFoundException(
                f"No Privacy Notice found for the application with uuid {application_uuid}"
            )
        return privacy_notice

    @staticmethod
    def write_privacy_notice_by_dc_or_dpo_id_and_application_uuid(
        user_id: int, application_uuid: UUID, content: str
    ) -> PrivacyNotice:
        """Writes a new `PrivacyNotice` for an `Application` if the `Application` with the given `UUID`
        exists and is managed by the given `DATA_CONTROLLER` or `DPO` user."

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the applications.
            application_uuid: The `UUID` of the `Application` to write the `PrivacyNotice` of.
            content: The content of the `PrivacyNotice` to be created.

        Returns:
            The newly created `PrivacyNotice` associated to the managed `Application` with the given `UUID`.

        Raises:
            `ApplicationNotFoundException`: If the `Application` with the given `UUID` is not found among the applications managed by the given `DATA_CONTROLLER` or `DPO` user.
            `PrivacyNoticeAlreadyExists`: If an already existing `PrivacyNotice` is found for the managed `Application` with the given `UUID`.
        """

        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        if application.privacy_notice:
            raise PrivacyNoticeAlreadyExists(
                f"Privacy Notice already exists for the application with uuid {application_uuid}"
            )
        return PrivacyNoticeRepository.create_privacy_notice(content, application.id)
