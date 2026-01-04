from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Tuple
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Room
from ..exceptions import RoomNotFoundException, RoomSyncException
from sqlalchemy import inspect
from sqlalchemy.orm import Mapper
from typing import cast



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
    ) -> dict[UUID, Room]:
        
        get_rooms_statement = db.select(Room).filter(Room.home_id == home_id)

        rooms_present = list(db.session.scalars(get_rooms_statement).all())

        rooms_dict_present: dict[UUID, Room] = {room.room_uuid: room for room in rooms_present}
        rooms_dict_input: dict[UUID, Room] = {room.room_uuid: room for room in rooms}
        mapper = cast(Mapper[Room], inspect(Room))

        for room_uuid, room in rooms_dict_input.items():
            room_present = rooms_dict_present.get(room_uuid)
            if room_present:
                # if the room is already present we update the values
                for attr in mapper.column_attrs:
                    if attr.key == "room_id":  # we don't update the primary key
                        continue
                    # update every attr of the Room from the database model
                    setattr(room_present, attr.key, getattr(room, attr.key))
            else:
                # if the room is not present we add it
                db.session.add(room)
                # we add it also to the room_dict_present
                rooms_dict_present[room_uuid] = room

        # removes rooms that have been deleted
        rooms_input_uuid = set(rooms_dict_input.keys())
        rooms_to_delete = list()
        for existing_uuid, existing_room in rooms_dict_present.items():
            if existing_uuid not in rooms_input_uuid:
                #also sets to null the room_id of all the devices in that room
                db.session.delete(existing_room)
                rooms_to_delete.append(existing_uuid)

        #removes all the old rooms from the dictionary
        for uuid in rooms_to_delete:
            del rooms_dict_present[uuid]
        
        #returns the updated dictionary with also the id of the rooms
        return rooms_dict_present
