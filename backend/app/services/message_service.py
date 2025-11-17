from typing import List, TypedDict
from uuid import UUID

from ..exceptions import UserNotFoundException
from ..models import Message, UserRole
from ..repositories import MessageRepository, UserRepository
from ..schemas import MessageReqSchema


class MessageReqDict(TypedDict):
    content: str
    attachment: str
    receiver_uuid: UUID


class MessageResDict(TypedDict):
    message: Message
    sender_uuid: UUID
    receiver_uuid: UUID


class MessageService:
    @staticmethod
    def get_messages_by_user_id_and_user_uuid(
        current_user_id: int, current_user_role: UserRole, other_user_uuid: UUID
    ) -> List[MessageResDict]:
        """Returns a list of messages fetched by a user's id and by another user's `UUID` from the database .

        Args:
            current_user_id: The ID of the user who exchanged messages with the other user.
            current_user_role: The role of the user who exchanged messages with the other user.
            other_user_uuid: The `UUID` of the other user with whom the user exchanged messages.

        Returns:
            A list of dictionaries each containing the message instance, the `UUID` of the sender and the `UUID` of the receiver, or an empty list if none are found.

        Raises:
            `UserNotFoundException`: If the other user with the given `UUID` is not found among the contacts of the given user.
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

    @staticmethod
    def send_message(
        sender_id: int,
        sender_role: UserRole,
        message: MessageReqSchema,
    ) -> MessageResDict:
        """Sends a message from a user to another user.

        Args:
            sender_id: The ID of the user who sends the message.
            sender_role: The role of the user who sends the message.
            message_data: A dictionary containing the content of the message,
                the optional attachment path, and the `UUID` of the receiver.

        Returns:
            A dictionary containing the message instance, the `UUID` of the sender and the `UUID` of the receiver.

        Raises:
            `UserNotFoundException`: If the other user with the given `UUID` is not found among the contacts of the given user.
        """

        receiver = UserRepository.get_contact_by_user_id_and_other_user_uuid(
            sender_id, message["receiver_uuid"]
        )
        if not receiver or (
            sender_role == UserRole.DATA_SUBJECT
            and receiver.role == UserRole.DATA_SUBJECT
        ):
            raise UserNotFoundException(
                f"User with uuid {message['receiver_uuid']} not found among the contacts!"
            )
        new_message = MessageRepository.create_message(
            message["content"],
            message["attachment"] if "attachment" in message else None,
            sender_id,
            receiver.id,
        )
        return {
            "message": new_message,
            "sender_uuid": new_message.sender.uuid,
            "receiver_uuid": new_message.receiver.uuid,
        }
