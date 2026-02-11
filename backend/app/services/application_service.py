import json
from datetime import datetime
from typing import List, TypedDict
from uuid import UUID

from jsonschema import ValidationError, validate
from sqlalchemy.exc import IntegrityError

from .. import initial_data
from ..exceptions import (
    ApplicationAlreadyAssignedException,
    ApplicationAlreadyExistsException,
    ApplicationNotFoundException,
    ApplicationNotManagedException,
    AvailableConsentWrongListException,
    DpoAlreadyAssignedException,
    InvalidApplicationNameException,
    InvalidPrivacyImpactAssessmentException,
    MissingDpoUuidException,
    MissingPrivacyImpactAssessmentException,
    MissingValidationSchemaException,
    PrivacyImpactAssessmentNotFoundException,
    SmartHomeNotFoundException,
    UserNotFoundException,
    WrongUserRoleException,
)
from ..models import Application
from ..repositories import (
    ApplicationRepository,
    AvailableConsentRepository,
    SmartHomeRepository,
    UserRepository,
)

from ..models import UserRole
from ..models import User
from .smartotum_service import SmartotumService
from ..integrations.marketplace import MarketplaceClient
from ..extensions import db


class ApplicationDict(TypedDict):
    application: Application
    installed_at: datetime

class ApplicationCatalogItem(TypedDict):
    application: Application
    data_controllers: list[User]
    dpo: User | None
    pn_status: str
    pia_status: str

class InstalledApplicationWithManagersDict(TypedDict):
    application: Application
    installed_at: datetime
    data_controllers: list[User]
    dpo: User | None
    pn_status: str
    pia_status: str


class ApplicationService:
    DOC_STATUS_AVAILABLE = "AVAILABLE"
    DOC_STATUS_MISSING = "MISSING"
    DOC_STATUS_FORBIDDEN = "FORBIDDEN"

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
                    "pn_status": (
                        ApplicationService.DOC_STATUS_AVAILABLE
                        if app.privacy_notice_id is not None
                        else ApplicationService.DOC_STATUS_MISSING
                    ),
                    "pia_status": ApplicationService.DOC_STATUS_FORBIDDEN,
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
    def get_pia_by_managed_application_uuid(user_id: int, application_uuid: str) -> dict:
        """Retrieves the Privacy Impact Assessment (PIA) of an application managed by a `DATA_CONTROLLER` or `DPO`, if any.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the application.
            application_uuid: The UUID of the application whose PIA is being requested.

        Returns:
            A dictionary containing the PIA data for the specified application.

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
        return privacy_impact_assessment

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
    def remove_pia_by_managed_application_uuid(user_id: int, application_uuid: str) -> None:
        """Removes an existing Privacy Impact Assessment (PIA) for an application managed by a `DATA_CONTROLLER` or `DPO`.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the application.
            application_uuid: The UUID of the application for which the PIA is being removed.

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
        if application.privacy_impact_assessment is None:
            raise PrivacyImpactAssessmentNotFoundException(
                f"No Privacy Impact Assessment found for the application with uuid {application_uuid}"
            )
        ApplicationRepository.remove_pia_for_application(application.id)

    @staticmethod
    def get_available_applications_service(current_user: User) -> List[ApplicationCatalogItem]:
        res = ApplicationRepository.get_available_application()
        catalog = {}

        for app, user in res:

            item = catalog.setdefault(
                app.id,
                {
                    "application": app,
                    "data_controllers": [],
                    "dpo": None,
                    "pn_status": ApplicationService.DOC_STATUS_FORBIDDEN,
                    "pia_status": ApplicationService.DOC_STATUS_FORBIDDEN,
                },
            )
            if not user:
                continue
            if user.role == UserRole.DATA_CONTROLLER:
                item["data_controllers"].append(user)
            elif item["dpo"] is None:
                item["dpo"] = user

        for item in catalog.values():
            is_managed_by_me = False
            if current_user.role == UserRole.DATA_CONTROLLER:
                is_managed_by_me = any(
                    dc.id == current_user.id for dc in item["data_controllers"]
                )
            elif current_user.role == UserRole.DATA_PROTECTION_OFFICER:
                is_managed_by_me = (
                    item["dpo"] is not None and item["dpo"].id == current_user.id
                )

            if not is_managed_by_me:
                continue

            app = item["application"]
            item["pn_status"] = (
                ApplicationService.DOC_STATUS_AVAILABLE
                if app.privacy_notice_id is not None
                else ApplicationService.DOC_STATUS_MISSING
            )
            item["pia_status"] = (
                ApplicationService.DOC_STATUS_AVAILABLE
                if app.privacy_impact_assessment is not None
                else ApplicationService.DOC_STATUS_MISSING
            )
        
        return list(catalog.values())
    


    @staticmethod
    def update_apps_database_from_all_sources(current_user: User):
        #if the user is a data subject we sync his homes with smartotum
        if current_user.role == UserRole.DATA_SUBJECT:
            #in case the update request comes from the refresh call
            SmartotumService.update_installed_application_for_user(current_user)
            #in the future a new domotic system can be added here
        else:
            client = MarketplaceClient()
            marketplace_applications = client.update_marketplace_applications()

            applications_payload: list[Application] = []
            for marketplace_application in marketplace_applications:
                applications_payload.append(
                    Application(
                        name=marketplace_application.name,
                        description=marketplace_application.description,
                    )
                )

            ApplicationRepository.upsert_applications(applications_payload)
            db.session.commit()

    #Permette ad un DC di creare un app e assegnarla automaticamente a se stesso
    @staticmethod
    def create_application_managed_by_data_controller(current_user: User,name: str,description: str | None = None,available_consents: list[str] | None = None,) -> ApplicationCatalogItem:
        
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        normalized_name = name.strip()
        if not normalized_name:
            raise InvalidApplicationNameException("Application name cannot be blank!")

        normalized_description = None
        if isinstance(description, str):
            description = description.strip()
            normalized_description = description if description else None

        normalized_available_consents: list[str] = []
        if available_consents is not None:
            for available_consent in available_consents:
                if not isinstance(available_consent, str):
                    raise AvailableConsentWrongListException("Available consents must be a list of non-empty strings!")
                normalized_available_consent = available_consent.strip()
                if not normalized_available_consent:
                    raise AvailableConsentWrongListException("Available consents must be a list of non-empty strings!")
                normalized_available_consents.append(normalized_available_consent)

            if len(normalized_available_consents) != len(set(normalized_available_consents)):
                raise AvailableConsentWrongListException("Duplicate consents selected!")

        existing_application = ApplicationRepository.get_application_by_name(
            normalized_name
        )
        if existing_application:
            raise ApplicationAlreadyExistsException(
                f"Application with name '{normalized_name}' already exists!"
            )

        try:
            application = ApplicationRepository.create_application(
                normalized_name, normalized_description
            )
            ApplicationRepository.ensure_application_managed_by_user(
                current_user.id, application.id
            )
            AvailableConsentRepository.upsert_available_consents_for_application(application.id, normalized_available_consents)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            #protezione da race condition (applicazione con lo stesso nome è stata aggiunta dopo
            #l'ultimo controllo)
            raise ApplicationAlreadyExistsException(
                f"Application with name '{normalized_name}' already exists!"
            )

        return {
            "application": application,
            "data_controllers": [current_user],
            "dpo": None,
            "pn_status": ApplicationService.DOC_STATUS_MISSING,
            "pia_status": ApplicationService.DOC_STATUS_MISSING,
        }

    @staticmethod
    def claim_application(
        current_user: User, application_uuid, force: bool = False
    ) -> bool:
        # Permette ad un Data Controller di "prendersi in carico" (claim) un'app
        # Se la relazione DC-App non esiste, la crea e ritorna True (201)
        # Se force=True, sostituisce l'eventuale Data Controller precedente.
        # Se force=False e la relazione esiste già, solleva errore.
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        application = ApplicationRepository.get_application_by_uuid(application_uuid)
        if not application:
            raise ApplicationNotFoundException(
                f"Application with uuid {application_uuid} not found!"
            )

        if force:
            created = ApplicationRepository.replace_data_controller_for_application(application.id, current_user.id)
            db.session.commit()
            return created

        #per il momento manteniamo il vecchio comportamento, possibile più di un data controller per app
        created = ApplicationRepository.ensure_application_managed_by_user(current_user.id, application.id)
        if not created:
            raise ApplicationAlreadyAssignedException(
                f"Application with uuid {application_uuid} is already assigned to this Data Controller!"
            )
        db.session.commit()
        return created

    @staticmethod
    def assign_dpo_to_managed_application(
        current_user: User,
        application_uuid,
        dpo_uuid: UUID | str | None = None,
    ) -> bool:
        # Assegna un DPO ad una app gestita da questo Data Controller.
        # Regole:
        # - il Data Controller deve già gestire l'app (altrimenti 403)
        # - dpo_uuid è obbligatorio (400)
        # - se l'app ha già un DPO diverso assegnato - 409
        # - se l'app ha già lo stesso DPO assegnato - ritorna False (204)
        # - se non c'è ancora un DPO assegnato - assegna e ritorna True (201)
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        managed_application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                current_user.id, application_uuid
            )
        )
        if not managed_application:
            raise ApplicationNotManagedException(
                f"Application with uuid {application_uuid} is not managed by the current Data Controller!"
            )

        if dpo_uuid is None:
            raise MissingDpoUuidException("dpo_uuid is required!")

        # Recuperiamo il DPO richiesto e verifichiamo che esista e abbia ruolo corretto.
        parsed_uuid = dpo_uuid
        if isinstance(parsed_uuid, str):
            parsed_uuid = UUID(parsed_uuid)
        dpo_user = UserRepository.get_user_by_uuid(parsed_uuid)
        if not dpo_user:
            raise UserNotFoundException(f"User with uuid {parsed_uuid} not found!")
        if dpo_user.role != UserRole.DATA_PROTECTION_OFFICER:
            raise WrongUserRoleException("User is not a Data Protection Officer!")

        # Se c'è già un DPO assegnato:
        # - se è lo stesso: no content (204)
        # - se è diverso: conflict (409)
        assigned_dpo_user_ids = ApplicationRepository.get_dpo_user_ids_for_application(
            managed_application.id
        )
        if assigned_dpo_user_ids and assigned_dpo_user_ids != {dpo_user.id}:
            raise DpoAlreadyAssignedException(
                "A different Data Protection Officer has already been assigned to this application!"
            )
        if assigned_dpo_user_ids == {dpo_user.id}:
            ApplicationRepository.assign_dpo_for_application(
                managed_application.id, dpo_user.id
            )
            db.session.commit()
            return False

        ApplicationRepository.assign_dpo_for_application(
            managed_application.id, dpo_user.id
        )
        db.session.commit()
        return True
