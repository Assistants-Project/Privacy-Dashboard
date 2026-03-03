import re

from sqlalchemy.exc import IntegrityError

from ..exceptions import (
    ApplicationAlreadyExistsException,
    AvailableConsentWrongListException,
    InvalidApplicationNameException,
    UserNotFoundException,
    WrongUserRoleException,
)
from ..extensions import db
from ..models import User, UserRole
from ..repositories import (
    ApplicationRepository,
    ConsentRepository,
    UserRepository,
)


class MarketplaceService:
    @staticmethod
    def register_marketplace_application(
        application_id: str,
        title: str,
        owner_email: str,
        delegates_email: list[str] | None = None,
        description: str | None = None,
        available_consents: list[str] | None = None,
    ) -> bool:
        normalized_application_id = application_id.strip()
        if not normalized_application_id:
            raise InvalidApplicationNameException("Application id cannot be blank!")
        if any(char.isspace() for char in normalized_application_id):
            raise InvalidApplicationNameException(
                "Application id must not contain spaces!"
            )
        if not re.fullmatch(r"com\.marketplace\.[a-z0-9-]+", normalized_application_id):
            raise InvalidApplicationNameException(
                "Application id must match 'com.marketplace.<slug>' (lowercase letters, numbers, '-')!"
            )

        normalized_title = title.strip()
        if not normalized_title:
            raise InvalidApplicationNameException("Application name cannot be blank!")

        normalized_description = None
        if isinstance(description, str):
            description = description.strip()
            normalized_description = description if description else None

        normalized_owner_email = owner_email.strip()
        owner_data_controller = UserRepository.get_user_by_email(normalized_owner_email)
        if not owner_data_controller:
            raise UserNotFoundException(
                f"User with email {normalized_owner_email} not found!"
            )
        if owner_data_controller.role != UserRole.DATA_CONTROLLER:
            raise WrongUserRoleException("User is not a Data Controller!")

        normalized_delegates_email: list[str] = []
        if delegates_email is not None:
            for delegate_email in delegates_email:
                if not isinstance(delegate_email, str):
                    raise WrongUserRoleException(
                        "Delegates must be valid Data Controller emails!"
                    )
                normalized_delegate_email = delegate_email.strip()
                if not normalized_delegate_email:
                    continue
                normalized_delegates_email.append(normalized_delegate_email)
        normalized_delegates_email = list(dict.fromkeys(normalized_delegates_email))
        normalized_delegates_email = [
            email
            for email in normalized_delegates_email
            if email != normalized_owner_email
        ]

        delegate_data_controllers: list[User] = []
        for delegate_email in normalized_delegates_email:
            delegate_data_controller = UserRepository.get_user_by_email(delegate_email)
            if not delegate_data_controller:
                raise UserNotFoundException(f"User with email {delegate_email} not found!")
            if delegate_data_controller.role != UserRole.DATA_CONTROLLER:
                raise WrongUserRoleException("User is not a Data Controller!")
            delegate_data_controllers.append(delegate_data_controller)

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
        normalized_available_consents = list(dict.fromkeys(normalized_available_consents))

        existing_application = ApplicationRepository.get_application_by_name(
            normalized_application_id
        )
        if existing_application:
            # Create only mode: once the app exists, the Privacy Dashboard becomes the source of truth
            # (including delegates and available consents). The marketplace can
            # safely send again the payload without overwriting local edits.
            if existing_application.owner_user_id != owner_data_controller.id:
                raise ApplicationAlreadyExistsException(
                    f"Application with id '{normalized_application_id}' already exists with a different owner!"
                )
            return False

        try:
            application = ApplicationRepository.create_application(
                normalized_application_id,
                normalized_description,
                title=normalized_title,
                owner_user_id=owner_data_controller.id,
            )
            ApplicationRepository.ensure_application_managed_by_user(
                owner_data_controller.id, application.id
            )
            for delegate_data_controller in delegate_data_controllers:
                ApplicationRepository.ensure_application_managed_by_user(
                    delegate_data_controller.id, application.id
                )
            ConsentRepository.upsert_available_consents_for_application(
                application.id, normalized_available_consents
            )
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ApplicationAlreadyExistsException(
                f"Application with id '{normalized_application_id}' already exists!"
            )
