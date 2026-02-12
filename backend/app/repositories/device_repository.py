from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator, List, Tuple, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Device
from ..exceptions import DeviceSyncException
from sqlalchemy import inspect
from sqlalchemy.orm import Mapper
from typing import cast
from sqlalchemy.orm import selectinload


class DeviceRepository:
    @staticmethod
    def get_device_by_home_id(
        home_id: int,
    ) -> List[Device]:
        statement = db.select(Device).filter(Device.home_id == home_id).options(selectinload(Device.room))
        
        return list(db.session.scalars(statement).all())
    
    @staticmethod
    def get_device_by_home_id_room_id(
        home_id: int,
        room_id: int
    ) -> List[Device]:
        statement = db.select(Device).filter(Device.home_id == home_id, Device.room_id == room_id).options(selectinload(Device.room))
        
        return list(db.session.scalars(statement).all())

    @staticmethod
    def update_device_for_home(
        home_id: int,
        devices: List[Device]
    ) -> None:
        
        get_devices_statement = db.select(Device).filter(Device.home_id == home_id)

        devices_present = list(db.session.scalars(get_devices_statement).all())

        devices_dict_present: dict[UUID, Device] = {device.device_uuid: device for device in devices_present}
        devices_dict_input: dict[UUID, Device] = {device.device_uuid: device for device in devices}
        mapper = cast(Mapper[Device], inspect(Device))

        # for every device in the input we check if it's present in our database
        for device_uuid, device in devices_dict_input.items():
            device_present = devices_dict_present.get(device_uuid)
            if device_present:
                # if the device is already present we update the values
                for attr in mapper.column_attrs:
                    if attr.key == "device_id":  # we don't update the primary key
                        continue
                    # update every attr of the Device from the database model
                    setattr(device_present, attr.key, getattr(device, attr.key))
            else:
                # if the device is not present we add it
                db.session.add(device)

        # removes devices that have been deleted
        devices_input_uuid = set(devices_dict_input.keys())
        for existing_uuid, existing_device in devices_dict_present.items():
            if existing_uuid not in devices_input_uuid:
                db.session.delete(existing_device)
    
    @staticmethod
    def get_device_by_uuid(device_uuid: str) -> Optional[Device]:
        """Get a device by its UUID"""
        statement = db.select(Device).filter(Device.device_uuid == device_uuid)
        return db.session.execute(statement).scalars().first()