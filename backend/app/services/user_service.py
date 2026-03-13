from typing import List, TypedDict
from uuid import UUID

from ..exceptions import ApplicationNotFoundException, UserNotFoundException
from ..models import User, UserRole
from ..repositories import ApplicationRepository, UserRepository
from ..services import MessageResDict, MessageService


class UserMessageResDict(TypedDict):
    user: User
    last_message: MessageResDict


class ContactApplicationResDict(TypedDict):
    uuid: UUID
    name: str
    title: str


class ContactResDict(TypedDict):
    user: User
    related_applications: List[ContactApplicationResDict]


class UserService:
    @staticmethod
    def get_user_by_uuid(uuid: UUID) -> User:
        """Returns a user fetched by its `UUID` from the database.

        Args:
            uuid: The `UUID` of the user to retrieve.

        Raises:
            `UserNotFoundException`: If no user with the given `UUID` is found in the database.
        """

        user = UserRepository.get_user_by_uuid(uuid)
        if not user:
            raise UserNotFoundException(f"User with uuid {uuid} not found")
        return user

    @staticmethod
    def get_users_by_dc_or_dpo_id_and_application_uuid_and_user_role(
        user_id: int, application_uuid: UUID, role: UserRole
    ) -> List[User]:
        """Returns the users of the given role associated with an `Application` if the `Application` with the given `UUID`
        exists and is managed by the given `DATA_CONTROLLER` or `DPO` user.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the applications.
            application_uuid: The UUID of the application to retrieve the users of.
            role: An enum that represents the role of the users to retrieve, one of `DATA_SUBJECT`, `DATA_CONTROLLER` and `DATA_PROTECTION_OFFICER`.

        Returns:
            The list of `User` instances of the given role associated with the `Application` except for the given user, or an empty list if none are found.

        Raises:
            `ApplicationNotFoundException`: If the application with the given `UUID` is not found among the applications managed by the  user.
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
        iterator = UserRepository.get_users_by_application_id_and_user_role(
            application.id, role
        )
        return [user for user in iterator if user.id != user_id]

    @staticmethod
    def get_contacts_by_user_id(user_id: int, role: UserRole) -> List[User]:
        """Returns the contacts of the given user. A contact, for
        a `DATA_CONTROLLER` or `DPO`, is any `User` of any role who has at least one managed or installed `Application`
        in common with the given `DATA_CONTROLLER` or `DPO`. A contact, for a `DATA_SUBJECT`, is any `User` of role
        `DATA_CONTROLLER` or `DPO` who has at least one managed `Application` in common with the given `DATA_SUBJECT`.

        Args:
            user_id: The ID of the user.
            role: The role of the user.

        Returns:
            The list of `User` instances that are contacts of the given user.
        """
        return [contact["user"] for contact in UserService.get_contact_items_by_user_id(user_id, role)]

    @staticmethod
    def get_contact_items_by_user_id(user_id: int, role: UserRole) -> List[ContactResDict]:
        rows = UserRepository.get_contacts_with_related_applications_by_user_id(user_id)
        contacts_by_id: dict[int, ContactResDict] = {}

        for contact, application in rows:
            if role == UserRole.DATA_SUBJECT and contact.role == role:
                continue

            if contact.id not in contacts_by_id:
                contacts_by_id[contact.id] = ContactResDict(
                    user=contact,
                    related_applications=[],
                )

            contacts_by_id[contact.id]["related_applications"].append(
                ContactApplicationResDict(
                    uuid=application.uuid,
                    name=application.name,
                    title=application.title,
                )
            )

        contacts = list(contacts_by_id.values())
        contacts.sort(
            key=lambda item: (
                item["user"].firstname.lower(),
                item["user"].lastname.lower(),
                item["user"].email.lower(),
            )
        )
        return contacts

    @staticmethod
    def get_messaged_contacts_by_user_id(
        user_id: int, role: UserRole
    ) -> List[UserMessageResDict]:
        """Returns the contacts of the given user who have exchanged at least one message with the user, along with the last exchanged message.

        Args:
            user_id: The ID of the user.
            role: The role of the user.

        Returns:
            A list of dictionaries each containing a `User` instance representing a contact who has exchanged at least one message with the user,
            and the last exchanged message as a `MessageResDict`.
        """

        contacts = UserService.get_contacts_by_user_id(user_id, role)
        messaged_contacts: List[UserMessageResDict] = []
        for contact in contacts:
            exchanged_messages = MessageService.get_messages_by_user_id_and_user_uuid(
                user_id, role, contact.uuid
            )
            if exchanged_messages:
                messaged_contacts.append(
                    UserMessageResDict(
                        user=contact, last_message=exchanged_messages[-1]
                    )
                )
        messaged_contacts.sort(
            key=lambda x: x["last_message"]["message"].sent_at, reverse=True
        )
        return messaged_contacts
