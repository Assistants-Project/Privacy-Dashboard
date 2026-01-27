import json
from datetime import datetime
from typing import List, TypedDict

from jsonschema import ValidationError, validate

from .. import initial_data
from ..exceptions import (
    ApplicationNotFoundException,
    InvalidPrivacyImpactAssessmentException,
    MissingPrivacyImpactAssessmentException,
    MissingValidationSchemaException,
    PrivacyImpactAssessmentNotFoundException,
    SmartHomeNotFoundException,
)
from ..models import Application
from ..repositories import ApplicationRepository, SmartHomeRepository

from ..models import UserRole
from ..models import User


class ApplicationDict(TypedDict):
    application: Application
    installed_at: datetime

class ApplicationCatalogItem(TypedDict):
    application: Application
    data_controllers: list[User]
    dpo: User | None

class InstalledApplicationWithManagersDict(TypedDict):
    application: Application
    installed_at: datetime
    data_controllers: list[User]
    dpo: User | None


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
    ) -> List[InstalledApplicationWithManagersDict]:
        """Returns a list of applications installed on a smart home identified by its UUID,
        along with the date and time they were installed and the assigned managers.

        Args:
            smart_home_uuid: The UUID of the smart home.
            user_id: The ID of the data subject requesting the information.

        Returns:
            A list of dictionaries each containing the application instance, the date and time it was installed
            on the specified smart home, and the assigned Data Controllers and DPOs.

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
        iterator = ApplicationRepository.get_installed_applications_with_managers_by_ds_id_and_smart_home_id(
            user_id, smart_home.id
        )
        installed: dict[int, InstalledApplicationWithManagersDict] = {}

        for app, installed_at, manager in iterator:
            item = installed.setdefault(
                app.id,
                {
                    "application": app,
                    "installed_at": installed_at,
                    "data_controllers": [],
                    "dpo": None,
                },
            )
            if manager is None:
                continue

            if manager.role == UserRole.DATA_CONTROLLER:
                item["data_controllers"].append(manager)
            elif manager.role == UserRole.DATA_PROTECTION_OFFICER:
                if item["dpo"] is None:
                    item["dpo"] = manager

        return list(installed.values())

    @staticmethod
    def get_pia_by_managed_application_uuid(user_id: int, application_uuid: str) -> str:
        """Retrieves the Privacy Impact Assessment (PIA) of an application managed by a `DATA_CONTROLLER` or `DPO`, if any.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the application.
            application_uuid: The UUID of the application whose PIA is being requested.

        Returns:
            A string representing a JSON-encoded dictionary containing the PIA data for the specified application.

        Raises:
            `ApplicationNotFoundException`: If the application with the given UUID is not found among the managed applications.
            `PrivacyImpactAssessmentNotFoundException`: If no PIA is found for the specified application.
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
        privacy_impact_assessment = application.privacy_impact_assessment
        if not privacy_impact_assessment:
            raise PrivacyImpactAssessmentNotFoundException(
                f"No Privacy Impact Assessment found for the application with uuid {application_uuid}"
            )
        return json.dumps(privacy_impact_assessment)

    @staticmethod
    def submit_pia_by_managed_application_uuid(
        user_id: int, application_uuid: str, submitted_pia_data: dict | None
    ) -> None:
        """Submits a Privacy Impact Assessment (PIA) for an application managed by a `DATA_CONTROLLER` or `DPO`.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the application.
            application_uuid: The UUID of the application for which the PIA is being submitted.
            submitted_pia_data: A dictionary containing the PIA data to be submitted, or `None` if no data is provided.

        Raises:
            `MissingPrivacyImpactAssessmentException`: If the `submitted_pia_data` is `None`.
            `MissingValidationSchemaException`: If the PIA JSON schema is not defined in the initial data.
            `InvalidPrivacyImpactAssessmentException`: If the submitted PIA data does not conform to the defined JSON schema.
            `ApplicationNotFoundException`: If the application with the given UUID is not found among the managed applications.
        """

        if submitted_pia_data is None:
            raise MissingPrivacyImpactAssessmentException(
                "JSON body with required Privacy Impact Assessment data is missing!"
            )
        if initial_data.pia_schema is None:
            raise MissingValidationSchemaException(
                "Privacy Impact Assessment JSON validation schema is not found!"
            )
        try:
            validate(instance=submitted_pia_data, schema=initial_data.pia_schema)
        except ValidationError as ve:
            raise InvalidPrivacyImpactAssessmentException(
                f"Submitted Privacy Impact Assessment data is invalid: {ve.message}"
            )
        application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                user_id, application_uuid
            )
        )
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found among the managed applications!"
            )
        ApplicationRepository.submit_pia_for_application(
            application.id, submitted_pia_data
        )

    @staticmethod
    def get_available_applications_service() -> List[ApplicationCatalogItem]:
        res = ApplicationRepository.get_available_application()
        catalog = {}

        for app, user in res:

            item = catalog.setdefault(
                app.id,
                {"application": app, "data_controllers": [], "dpo": None},
            )
            if not user:
                continue
            if user.role == UserRole.DATA_CONTROLLER:
                item["data_controllers"].append(user)
            elif item["dpo"] is None:
                item["dpo"] = user
        
        return list(catalog.values())
