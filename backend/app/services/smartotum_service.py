from typing import Any
from uuid import UUID

from flask import request

from ..exceptions import MissingJWTException, WrongUserCredentialsException
from ..exceptions.entities.smart_home_exception import SmartHomeNotFoundException
from ..integrations.smartotum import SmartotumClient
from ..repositories.room_repository import RoomRepository
from ..repositories.smart_home_repository import SmartHomeRepository
from ..models import Room
from ..models import User
from ..models import SmartHome
from ..models import Device
from ..repositories.device_repository import DeviceRepository
from ..exceptions.entities.room_exceptions import RoomPersistenceException

class SmartotumService:

    @staticmethod
    def update_database(access_token: str, user: User):

        client = SmartotumClient()
        systems = client.get_systems(access_token)

        for system in systems:
            home = SmartHomeRepository.upsert_home(system.home_uuid, system.name, system.address)
            SmartHomeRepository.assign_home(home.id,user.id)
            rooms = client.get_home_rooms(access_token, system.home_uuid)

            #to avoid to much traffic to the database we send all the rooms
            normalized_rooms=[]

            for room in rooms:

                normalized_rooms.append(
                    Room(
                        room_uuid=room.room_uuid,
                        name=room.name,
                        home_id=home.id,
                        category=room.category
                    )
                )

            RoomRepository.update_rooms_for_home(home.id, normalized_rooms)

            #now we update all the devices for every home
            devices = client.get_home_devices(access_token, system.home_uuid)

            normalized_devices = []

            for device in devices:
                if not device.room_uuid:
                    continue

                room = RoomRepository.get_room_by_uuid(device.room_uuid)
                if not room:
                    raise RoomPersistenceException("Room not found")

                normalized_devices.append(
                    Device(
                        device_uuid=device.device_uuid,
                        home_id=home.id,
                        room_id=room.room_id,
                        name=device.name,
                        topic_name=device.topic_name

                    )
                )

            if normalized_devices:
                DeviceRepository.update_device_for_home(home.id, normalized_devices)


        return

    @staticmethod
    def update_database_for_user(user: User):
        access_token = request.cookies.get("st_access_token")
        if not access_token:
            raise MissingJWTException("Smartotum access token missing")

        SmartotumService.update_database(access_token, user)
    
    #gets the homes of the current user
    @staticmethod
    def get_homes(current_user: User) -> list[SmartHome]:

        return SmartHomeRepository.get_homes_by_user_id(current_user.id)
    
    
    @staticmethod
    def get_home_rooms(system_uuid: str) -> list[Room]:

        system = SmartHomeRepository.get_home_by_uuid(system_uuid)

        if system is None:
            raise SmartHomeNotFoundException("Smart Home Not Found")

        return RoomRepository.get_rooms_by_home_id(system.id)

    @staticmethod
    def get_home_devices(system_uuid: str) -> list[Device]:

        system = SmartHomeRepository.get_home_by_uuid(system_uuid)

        if system is None:
            raise SmartHomeNotFoundException("Smart Home Not Found")

        return DeviceRepository.get_device_by_home_id(system.id)
    
    @staticmethod
    def get_home_room_devices(system_uuid: str, room_uuid: str) -> list[Device]:

        system = SmartHomeRepository.get_home_by_uuid(system_uuid)

        if system is None:
            raise SmartHomeNotFoundException("Smart Home Not Found")
        
        room = RoomRepository.get_room_by_uuid(UUID(room_uuid))

        if room is None:
            raise RoomPersistenceException("Room not found")

        return DeviceRepository.get_device_by_home_id_room_id(system.id,room.room_id)
