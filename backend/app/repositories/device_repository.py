from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Tuple
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Room
from ..models import SmartHome
from ..models import Device
from ..exceptions import RoomPersistenceException


class DeviceRepository:
    @staticmethod
    def get_device_by_home_id(
        home_id: int,
    ) -> List[Device]:
        statement = db.select(Device).filter(Device.home_id == home_id)
        
        return list(db.session.scalars(statement).all())
    
    @staticmethod
    def get_device_by_home_id_room_id(
        home_id: int,
        room_id: int
    ) -> List[Device]:
        statement = db.select(Device).filter(Device.home_id == home_id, Device.room_id == room_id)
        
        return list(db.session.scalars(statement).all())

    @staticmethod
    def update_device_for_home(
        home_id: int,
        devices: List[Device]
    ) -> None:
        
        try:
            db.session.query(Device).filter(Device.home_id == home_id).delete()

            for device in devices:
                db.session.add(device)

            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise RoomPersistenceException("Unable to update device for smart home") from exc

