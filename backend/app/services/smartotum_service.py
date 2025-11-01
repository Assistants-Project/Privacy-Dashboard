from typing import Any
from uuid import UUID

from flask import request

from ..exceptions import MissingJWTException, WrongUserCredentialsException
from ..exceptions.entities.home_exception import SmartHomeNotFoundException
from ..integrations.smartotum import SmartotumClient
from ..repositories.room_repository import RoomRepository
from ..repositories.smart_home_repository import SmartHomeRepository
from ..models import Room
from ..models import User
from ..models import SmartHome
from ..models import Device
from ..repositories.device_repository import DeviceRepository
from ..exceptions.entities.room_exceptions import RoomNotFoundException

class SmartotumService:

    @staticmethod
    def update_database_smartotum(access_token: str, user: User):

        client = SmartotumClient()
        #get system list of the user
        systems = client.get_systems(access_token)

        #for ever home owned by the user
        for system in systems:
            #insert or update the home
            home = SmartHomeRepository.upsert_home(system.home_uuid, system.name, system.address)
            #assign the home to the user
            SmartHomeRepository.assign_home(home.id,user.id)
            #get all the rooms of the home from smartotum
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

            #it deletes all the rooms of the house and insert them again, now updated
            RoomRepository.update_rooms_for_home(home.id, normalized_rooms)

            #now we update all the devices for every home
            #get all the home devices from smartotum
            devices = client.get_home_devices(access_token, system.home_uuid)

            normalized_devices = []

            for device in devices:
                
                #if the device does not have a room for now we don't save it
                if not device.room_uuid:
                    continue

                #get the id of the room
                room = RoomRepository.get_room_by_uuid(device.room_uuid)

                #should not happen, rooms should already by updated
                if not room:
                    raise RoomNotFoundException("Room not found")
                
                #add the device to the list of devices
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
                #add all the devices
                DeviceRepository.update_device_for_home(home.id, normalized_devices)


        return

    @staticmethod
    def update_database_smartotum_for_user(user: User):
        access_token = request.cookies.get("st_access_token")
        if not access_token:
            raise MissingJWTException("Smartotum access token missing")

        SmartotumService.update_database_smartotum(access_token, user)