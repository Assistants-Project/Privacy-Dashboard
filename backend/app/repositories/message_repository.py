from typing import Iterator

from ..extensions import db
from ..models import Message


class MessageRepository:
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#select-in-loading
    @staticmethod
    def get_messages_by_user_ids(
        first_user_id: int, second_user_id: int
    ) -> Iterator[Message]:
        statement = (
            db.select(Message)
            .options(db.selectinload(Message.sender), db.selectinload(Message.receiver))
            .where(
                db.or_(
                    db.and_(
                        Message.sender_id == first_user_id,
                        Message.receiver_id == second_user_id,
                    ),
                    db.and_(
                        Message.sender_id == second_user_id,
                        Message.receiver_id == first_user_id,
                    ),
                )
            )
            .order_by(Message.sent_at)
        )
        return db.session.scalars(statement)
