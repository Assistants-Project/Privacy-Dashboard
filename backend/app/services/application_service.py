from datetime import datetime
from typing import List, TypedDict

from ..exceptions import ApplicationNotFoundException, SmartHomeNotFoundException
from ..models import Application
from ..repositories import ApplicationRepository, SmartHomeRepository


class ApplicationDict(TypedDict):
    application: Application
    installed_at: datetime


class ApplicationService:
    @staticmethod
    def get_applications_by_dc_or_dpo_id(
        user_id: int,
    ) -> List[ApplicationDict]:
        """Returns a list of applications fetched by a `DATA_CONTROLLER` or `DPO`'s id from the database,
        along with the date and time they were installed.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the applications.

        Returns:
            A list of dictionaries each containing the application instance and the date and time it was installed
            by the given user, or an empty list if none are found.
        """

        iterator = ApplicationRepository.get_applications_by_dc_or_dpo_id(user_id)
        return [{"application": app, "installed_at": dt} for app, dt in iterator]

    @staticmethod
    def get_applications_by_ds_id_and_smart_home_uuid(
        user_id: int, smart_home_uuid: str
    ) -> List[ApplicationDict]:
        """Returns a list of applications installed on a smart home identified by its UUID,
        along with the date and time they were installed.

        Args:
            smart_home_uuid: The UUID of the smart home.
            user_id: The ID of the data subject requesting the information.

        Returns:
            A list of dictionaries each containing the application instance and the date and time it was installed
            on the specified smart home, or an empty list if none are found.

        Raises:
            `SmartHomeNotFoundException`: If the `SmartHome` with the given `UUID` is not found among the owned smart homes.
        """

        smart_home = SmartHomeRepository.get_home_by_ds_id_and_home_uuid(
            user_id, smart_home_uuid
        )
        if not smart_home:
            raise SmartHomeNotFoundException(
                f"Smart Home with uuid {smart_home_uuid} not found among the owned smart homes!"
            )
        iterator = ApplicationRepository.get_applications_by_ds_id_and_smart_home_id(
            user_id, smart_home.id
        )
        return [{"application": app, "installed_at": dt} for app, dt in iterator]

    @staticmethod
    def submit_pia_by_managed_application_uuid(
        user_id: int, application_uuid: str, pia_data: dict
    ) -> None:
        """Submits a Privacy Impact Assessment (PIA) for an application managed by a `DATA_CONTROLLER` or `DPO`.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the application.
            application_uuid: The UUID of the application for which the PIA is being submitted.
            pia_data: A dictionary containing the PIA data to be submitted.

        Raises:
            `ApplicationNotFoundException`: If the application with the given UUID is not found among the managed applications.
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
        # TODO: add validation of pia_data json schema
        ApplicationRepository.submit_pia_for_application(application.id, pia_data)
