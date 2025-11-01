from typing import Any
from uuid import UUID

from flask import request

from ..exceptions import MissingJWTException, WrongUserCredentialsException
from ..exceptions.entities.home_exception import SmartHomeNotFoundException
from ..exceptions.entities.home_exception import SmartHomeForbiddenException
from ..integrations.smartotum import SmartotumClient
from ..repositories.room_repository import RoomRepository
from ..repositories.smart_home_repository import SmartHomeRepository
from ..models import Room
from ..models import User
from ..models import UserRole
from ..models import SmartHome
from ..models import Device
from ..repositories.device_repository import DeviceRepository
from ..exceptions.entities.room_exceptions import RoomNotFoundException
from .smartotum_service import SmartotumService


class SmartHomeService:

    @staticmethod
    def update_database_for_user(current_user: User):
        #if the user is a data subject we sync is homes with smartotum
        if current_user.role == UserRole.DATA_SUBJECT:
            SmartotumService.update_database_smartotum_for_user(current_user)
            #in the future a new domotic system can be added here

    #gets the homes of the current user
    @staticmethod
    def get_homes(current_user: User) -> list[SmartHome]:

        return SmartHomeRepository.get_homes_by_user_id(current_user.id)
    
    #gets the rooms of the requested home
    @staticmethod
    def get_home_rooms(system_uuid: str, current_user: User) -> list[Room]:
        system = SmartHomeRepository.get_home_by_uuid(system_uuid)

        if system is None:
            raise SmartHomeNotFoundException("Smart Home Not Found")

        owners: list[int] = SmartHomeRepository.get_home_owners_by_home_id(system.id)
        
        if current_user.id not in owners:
            raise SmartHomeForbiddenException("User does not have access to the smarthome")


        return RoomRepository.get_rooms_by_home_id(system.id)
    
    #gets the devices of the requested home
    @staticmethod
    def get_home_devices(system_uuid: str, current_user: User) -> list[Device]:

        system = SmartHomeRepository.get_home_by_uuid(system_uuid)

        if system is None:
            raise SmartHomeNotFoundException("Smart Home Not Found")
        
        owners: list[int] = SmartHomeRepository.get_home_owners_by_home_id(system.id)
        
        if current_user.id not in owners:
            raise SmartHomeForbiddenException("User does not have access to the smarthome")

        return DeviceRepository.get_device_by_home_id(system.id)
    
    #gets the devices of the requested room inside the requested house
    @staticmethod
    def get_home_room_devices(system_uuid: str, room_uuid: str, current_user: User) -> list[Device]:

        system = SmartHomeRepository.get_home_by_uuid(system_uuid)

        if system is None:
            raise SmartHomeNotFoundException("Smart Home Not Found")
        
        owners: list[int] = SmartHomeRepository.get_home_owners_by_home_id(system.id)
        
        if current_user.id not in owners:
            raise SmartHomeForbiddenException("User does not have access to the smarthome")
        
        room = RoomRepository.get_room_by_uuid(UUID(room_uuid))

        if room is None:
            raise RoomNotFoundException("Room not found")

        return DeviceRepository.get_device_by_home_id_room_id(system.id,room.room_id)
