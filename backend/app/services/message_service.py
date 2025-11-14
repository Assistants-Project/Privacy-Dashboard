from typing import List, TypedDict
from uuid import UUID

from ..exceptions import UserNotFoundException
from ..models import Message, UserRole
from ..repositories import MessageRepository, UserRepository


class MessageDict(TypedDict):
    message: Message
    sender_uuid: UUID
    receiver_uuid: UUID


class MessageService:
    @staticmethod
    def get_messages_by_user_id_and_user_uuid(
        current_user_id: int, other_user_uuid: UUID, current_user_role: UserRole
    ) -> List[MessageDict]:
        """Returns a list of messages fetched by a user's id and by another user's `UUID` from the database .

        Args:
            current_user_id: The ID of the user who exchanged messages with the other user.
            other_user_uuid: The `UUID` of the other user with whom the user exchanged messages.
            current_user_role: The role of the user who exchanged messages with the other user.

        Returns:
            A list of dictionaries each containing the message instance, the `UUID` of the sender and the `UUID` of the receiver, or an empty list if none are found.

        Raises:
            `UserNotFoundException`: If the user with the given `UUID` is not found among the contacts of the given `DATA_CONTROLLER` or `DPO` user.
        """

        other_user = UserRepository.get_contact_by_user_id_and_other_user_uuid(
            current_user_id, other_user_uuid
        )
        if not other_user or (
            current_user_role == UserRole.DATA_SUBJECT
            and other_user.role == UserRole.DATA_SUBJECT
        ):
            raise UserNotFoundException(
                f"User with uuid {other_user_uuid} not found among the contacts!"
            )
        iterator = MessageRepository.get_messages_by_user_ids(
            current_user_id, other_user.id
        )
        return [
            {
                "message": message,
                "sender_uuid": message.sender.uuid,
                "receiver_uuid": message.receiver.uuid,
            }
            for message in iterator
        ]
