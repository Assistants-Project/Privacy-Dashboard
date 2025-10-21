from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Tuple
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Room
from ..exceptions import RoomPersistenceException


class RoomRepository:
    @staticmethod
    def get_room_by_uuid(room_uuid: UUID) -> Room | None:

        statement = db.select(Room).filter(Room.room_uuid == room_uuid)

        return db.session.scalar(statement)
    
    @staticmethod
    def get_rooms_by_home_id(
        home_id: int,
    ) -> List[Room]:
        statement = db.select(Room).filter(Room.home_id == home_id)
        
        return list(db.session.scalars(statement).all())

    @staticmethod
    def update_rooms_for_home(
        home_id: int,
        rooms: List[Room]
    ) -> None:
        
        try:
            db.session.query(Room).filter(Room.home_id == home_id).delete()

            for room in rooms:
                db.session.add(room)

            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise RoomPersistenceException("Unable to update rooms for smart home") from exc
