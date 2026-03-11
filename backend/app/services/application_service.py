import re
from datetime import datetime
from typing import List, TypedDict
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from ..exceptions import ApplicationAlreadyExistsException, ApplicationNotManagedException, InvalidApplicationNameException, MissingDpoUuidException, SmartHomeNotFoundException, UserNotFoundException, WrongUserRoleException
from ..models import Application
from ..repositories import ApplicationRepository, ConsentRepository, SmartHomeRepository, UserRepository
from ..models import UserRole
from ..models import User
from ..extensions import db
from .consent_service import normalize_available_consents_payload


class ApplicationItem(TypedDict):
    application: Application
    owner: User | None
    data_controllers: list[User]
    dpo: User | None
    pn_status: str
    pia_status: str
    pending_right_requests_count: int


class ManagedApplicationItem(ApplicationItem):
    pass


class InstalledApplicationItem(ApplicationItem):
    installed_at: datetime


class ApplicationService:

    MANUAL_APPLICATION_ID_PREFIX = "com.privacydashboard."
    DOC_STATUS_AVAILABLE = "AVAILABLE"
    DOC_STATUS_MISSING = "MISSING"

    @staticmethod
    def _is_manual_application_name(application_name: str) -> bool:
        return application_name.startswith(ApplicationService.MANUAL_APPLICATION_ID_PREFIX)

    @staticmethod
    def _get_owned_managed_application(current_user: User, application_uuid) -> Application:
        managed_application = (
            ApplicationRepository.get_application_by_user_id_and_application_uuid(
                current_user.id, application_uuid
            )
        )
        if not managed_application:
            raise ApplicationNotManagedException(
                f"Application with uuid {application_uuid} is not managed by the current Data Controller!"
            )
        if managed_application.owner_user_id != current_user.id:
            raise ApplicationNotManagedException(
                f"Application with uuid {application_uuid} is not owned by the current Data Controller!"
            )
        return managed_application

    @staticmethod
    def get_applications_by_dc_or_dpo_id(current_user: User, application_uuid: UUID | None = None) -> List[ManagedApplicationItem]:
        """Returns a list of applications fetched by a `DATA_CONTROLLER` or `DPO`'s id from the database,
        along with the date and time they were installed.

        Args:
            current_user: The user with role `DATA_CONTROLLER` or `DPO` who manages the applications.
            application_uuid: Optional UUID of a specific managed application to retrieve.

        Returns:
            A list of managed applications with owner, managers and documents status.
        """
        res = ApplicationRepository.get_applications_by_dc_or_dpo_id(current_user.id, application_uuid)
        managed_applications: dict[int, ManagedApplicationItem] = {}

        for app, _installed_at, manager in res:
            item = managed_applications.setdefault(
                app.id,
                {
                    "application": app,
                    "owner": app.owner,
                    "data_controllers": [],
                    "dpo": None,
                    "pn_status": (
                        ApplicationService.DOC_STATUS_AVAILABLE
                        if app.privacy_notice_id is not None
                        else ApplicationService.DOC_STATUS_MISSING
                    ),
                    "pia_status": (
                        ApplicationService.DOC_STATUS_AVAILABLE
                        if app.privacy_impact_assessment is not None
                        else ApplicationService.DOC_STATUS_MISSING
                    ),
                    "pending_right_requests_count": 0,
                },
            )
            if manager is None:
                continue
            if manager.role == UserRole.DATA_CONTROLLER:
                if not any(dc.id == manager.id for dc in item["data_controllers"]):
                    item["data_controllers"].append(manager)
            elif manager.role == UserRole.DATA_PROTECTION_OFFICER and item["dpo"] is None:
                item["dpo"] = manager

        pending_request_counts = (
            ApplicationRepository.get_pending_request_counts_for_managed_applications(
                list(managed_applications.keys())
            )
        )
        for application_id, item in managed_applications.items():
            item["pending_right_requests_count"] = pending_request_counts.get(
                application_id, 0
            )

        return list(managed_applications.values())

    @staticmethod
    def get_applications_by_ds_id_and_smart_home_uuid(
        user_id: int, smart_home_uuid: str, application_uuid: UUID | None = None
    ) -> List[InstalledApplicationItem]:
        """Returns a list of applications installed on a smart home identified by its UUID,
        along with the date and time they were installed and the assigned managers.

        Args:
            smart_home_uuid: The UUID of the smart home.
            user_id: The ID of the data subject requesting the information.
            application_uuid: Optional UUID of a specific installed application to retrieve.

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
            user_id, smart_home.id, application_uuid
        )
        installed: dict[int, InstalledApplicationItem] = {}

        for app, installed_at, manager in iterator:
            item = installed.setdefault(
                app.id,
                {
                    "application": app,
                    "installed_at": installed_at,
                    "owner": app.owner,
                    "data_controllers": [],
                    "dpo": None,
                    "pn_status": (
                        ApplicationService.DOC_STATUS_AVAILABLE
                        if app.privacy_notice_id is not None
                        else ApplicationService.DOC_STATUS_MISSING
                    ),
                    "pia_status": (
                        ApplicationService.DOC_STATUS_AVAILABLE
                        if app.privacy_impact_assessment is not None
                        else ApplicationService.DOC_STATUS_MISSING
                    ),
                    "pending_right_requests_count": 0,
                },
            )
            if manager is None:
                continue

            if manager.role == UserRole.DATA_CONTROLLER:
                item["data_controllers"].append(manager)
            elif manager.role == UserRole.DATA_PROTECTION_OFFICER:
                if item["dpo"] is None:
                    item["dpo"] = manager

        pending_request_counts = (
            ApplicationRepository.get_pending_request_counts_for_installed_applications(
                user_id, smart_home.uuid, list(installed.keys())
            )
        )
        for application_id, item in installed.items():
            item["pending_right_requests_count"] = pending_request_counts.get(
                application_id, 0
            )

        return list(installed.values())

    #Permette ad un DC di creare un app e assegnarla automaticamente a se stesso
    @staticmethod
    def create_application_managed_by_data_controller(current_user: User,id: str,title: str,description: str | None = None,available_consents: list[str] | None = None,) -> ManagedApplicationItem:
        
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        normalized_id = id.strip()
        if not normalized_id:
            raise InvalidApplicationNameException("Application id cannot be blank!")
        if not re.fullmatch(r"[A-Za-z0-9-]+", normalized_id):
            raise InvalidApplicationNameException(
                "Application id can contain only letters, numbers and '-'!"
            )

        application_id = f"{ApplicationService.MANUAL_APPLICATION_ID_PREFIX}{normalized_id}"
        application_title = title.strip()
        if not application_title:
            raise InvalidApplicationNameException("Application title cannot be blank!")

        normalized_description = None
        if isinstance(description, str):
            description = description.strip()
            normalized_description = description if description else None

        normalized_available_consents = normalize_available_consents_payload(available_consents, deduplicate=False)

        existing_application = ApplicationRepository.get_application_by_name(
            application_id
        )
        if existing_application:
            raise ApplicationAlreadyExistsException(
                f"Application with id '{application_id}' already exists!"
            )

        try:
            application = ApplicationRepository.create_application(
                application_id,
                normalized_description,
                title=application_title,
                owner_user_id=current_user.id,
            )
            ApplicationRepository.ensure_application_managed_by_user(
                current_user.id, application.id
            )
            ConsentRepository.upsert_available_consents_for_application(application.id, normalized_available_consents)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            #protezione da race condition (applicazione con lo stesso nome è stata aggiunta dopo
            #l'ultimo controllo)
            raise ApplicationAlreadyExistsException(
                f"Application with id '{application_id}' already exists!"
            )

        return {
            "application": application,
            "owner": current_user,
            "data_controllers": [current_user],
            "dpo": None,
            "pn_status": ApplicationService.DOC_STATUS_MISSING,
            "pia_status": ApplicationService.DOC_STATUS_MISSING,
            "pending_right_requests_count": 0,
        }

    @staticmethod
    def update_owned_manual_application(current_user: User, application_uuid, title: str, description: str | None = None) -> ManagedApplicationItem:
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        managed_application = ApplicationService._get_owned_managed_application(current_user, application_uuid)
        if not ApplicationService._is_manual_application_name(managed_application.name):
            raise ApplicationNotManagedException(
                "Only applications created in the Privacy Dashboard can be edited."
            )

        normalized_title = title.strip()
        if not normalized_title:
            raise InvalidApplicationNameException("Application title cannot be blank!")

        normalized_description = None
        if isinstance(description, str):
            description = description.strip()
            normalized_description = description if description else None

        managed_application.title = normalized_title
        managed_application.description = normalized_description
        db.session.commit()

        return ApplicationService.get_applications_by_dc_or_dpo_id(current_user, managed_application.uuid)[0]

    @staticmethod
    def assign_dpo_to_managed_application(
        current_user: User,
        application_uuid,
        dpo_email: str | None = None,
    ) -> str:
        # Assegna o sostituisce il DPO di una app gestita da questo Data Controller.
        # Regole:
        # - il Data Controller deve già gestire l'app (altrimenti 403)
        # - dpo_email è obbligatorio (400)
        # - se l'app ha già lo stesso DPO assegnato - ritorna "unchanged" (204)
        # - se non c'è ancora un DPO assegnato - ritorna "created" (201)
        # - se esiste un DPO diverso - ritorna "replaced" (200)
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        managed_application = ApplicationService._get_owned_managed_application(
            current_user, application_uuid
        )

        if dpo_email is None:
            raise MissingDpoUuidException("dpo_email is required!")

        normalized_dpo_email = dpo_email.strip()
        if not normalized_dpo_email:
            raise MissingDpoUuidException("dpo_email is required!")

        # Recuperiamo il DPO richiesto e verifichiamo che esista e abbia ruolo corretto.
        dpo_user = UserRepository.get_user_by_email(normalized_dpo_email)
        if not dpo_user:
            raise UserNotFoundException(
                f"User with email {normalized_dpo_email} not found!"
            )
        if dpo_user.role != UserRole.DATA_PROTECTION_OFFICER:
            raise WrongUserRoleException("User is not a Data Protection Officer!")

        assigned_dpo_user_ids = ApplicationRepository.get_dpo_user_ids_for_application(
            managed_application.id
        )
        had_dpo = bool(assigned_dpo_user_ids)
        changed = assigned_dpo_user_ids != {dpo_user.id}
        ApplicationRepository.assign_dpo_for_application(
            managed_application.id, dpo_user.id
        )
        db.session.commit()
        if not changed:
            return "unchanged"
        if had_dpo:
            return "replaced"
        return "created"

    @staticmethod
    def remove_dpo_from_managed_application(current_user: User, application_uuid) -> bool:
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        managed_application = ApplicationService._get_owned_managed_application(
            current_user, application_uuid
        )
        removed = ApplicationRepository.remove_dpo_for_application(managed_application.id)
        db.session.commit()
        return removed

    @staticmethod
    def add_data_controller_manager_to_owned_application(current_user: User, application_uuid, user_email: str) -> bool:
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        managed_application = ApplicationService._get_owned_managed_application(
            current_user, application_uuid
        )

        normalized_user_email = user_email.strip()
        data_controller = UserRepository.get_user_by_email(normalized_user_email)
        if not data_controller:
            raise UserNotFoundException(
                f"User with email {normalized_user_email} not found!"
            )
        if data_controller.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        created = ApplicationRepository.ensure_application_managed_by_user(
            data_controller.id, managed_application.id
        )
        db.session.commit()
        return created

    @staticmethod
    def remove_data_controller_manager_from_owned_application(current_user: User, application_uuid, user_email: str) -> bool:
        if current_user.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        managed_application = ApplicationService._get_owned_managed_application(
            current_user, application_uuid
        )

        normalized_user_email = user_email.strip()
        data_controller = UserRepository.get_user_by_email(normalized_user_email)
        if not data_controller:
            raise UserNotFoundException(
                f"User with email {normalized_user_email} not found!"
            )
        if data_controller.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")
        if data_controller.id == managed_application.owner_user_id:
            raise ApplicationNotManagedException(
                "Cannot remove the owner from application managers."
            )

        removed = ApplicationRepository.remove_application_managed_by_user(
            data_controller.id, managed_application.id
        )
        db.session.commit()
        return removed
