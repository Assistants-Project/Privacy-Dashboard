from uuid import UUID

from flask import request
from sqlalchemy.exc import SQLAlchemyError

from ..exceptions import MissingJWTException, SmartotumSyncException
from ..integrations.smartotum import SmartotumClient
from ..repositories.room_repository import RoomRepository
from ..repositories.smart_home_repository import SmartHomeRepository
from ..models import Room
from ..models import User
from ..models import SmartHome
from ..models import Device
from ..repositories.device_repository import DeviceRepository
from ..exceptions.entities.room_exceptions import RoomNotFoundException
from ..extensions import db
from ..integrations.smartotum.client import SmartotumRule
from typing import List

class SmartotumService:

    @staticmethod
    def update_database_smartotum(access_token: str, user: User):
        #for now it doesn't update rules and application, waiting for a database implementation for rules by the PTP app
        session = db.session
        try:
            client = SmartotumClient()
            #get system list of the user
            systems_new = client.get_systems(access_token)
            new_homes_uuid = set()

            #for ever home owned by the user
            for system in systems_new:
                new_homes_uuid.add(system.home_uuid)
                #insert or update the home
                home = SmartHomeRepository.upsert_home(system.home_uuid, system.name, system.address)
                #assign the home to the user
                SmartHomeRepository.assign_home(home.id,user.id)
                #get all the rooms of the home from smartotum
                rooms = client.get_home_rooms(access_token, system.home_uuid)

                #to avoid to much traffic to the database we send all the rooms
                rooms_payload=[]

                #special room to contain all the devices that don't have one
                special_room_uuid = UUID(int=0)

                rooms_payload.append(
                    Room(
                        room_uuid=special_room_uuid,
                        #special room with the same name as the house
                        name=system.name,
                        home_id=home.id,
                        category="House"
                    )
                )

                for room in rooms:

                    rooms_payload.append(
                        Room(
                        room_uuid=room.room_uuid,
                        name=room.name,
                        home_id=home.id,
                        category=room.category
                        )
                    )

                #updates the room of the house
                updated_rooms: dict[UUID, Room] = RoomRepository.update_rooms_for_home(home.id, rooms_payload)

                special_room = updated_rooms.get(special_room_uuid)
                if special_room is None:
                    raise SmartotumSyncException("Special room not found after sync")

                #now we update all the devices for every home
                #get all the home devices from smartotum
                devices = client.get_home_devices(access_token, system.home_uuid)

                updated_devices = []

                for device in devices:
                
                    #if the device does not have a room for now we don't save it
                    #TODO: add a special room for devices that don't have it
                    if not device.room_uuid:

                        new_device = Device(
                        device_uuid=device.device_uuid,
                        home_id=home.id,
                        name=device.name,
                        topic_name=device.topic_name
                        )

                        new_device.room = special_room #link device to the special room

                        #add the device to the list of devices
                        updated_devices.append(new_device)

                        continue

                    #get the room of the device
                    room = updated_rooms.get(device.room_uuid)

                    #should not happen, rooms should already by updated
                    if not room:
                        raise RoomNotFoundException("Room not found")
                
                    new_device = Device(
                        device_uuid=device.device_uuid,
                        home_id=home.id,
                        name=device.name,
                        topic_name=device.topic_name
                    )
                    new_device.room = room #link device to room

                    #add the device to the list of devices
                    updated_devices.append(new_device)

                #update all the devices of the home, even if there are none
                DeviceRepository.update_device_for_home(home.id, updated_devices)

            existing_home: list[SmartHome] = SmartHomeRepository.get_homes_by_user_id(user.id)

            for home in existing_home:
                if home.uuid not in new_homes_uuid:
                    SmartHomeRepository.delete_home(home)
            
            session.commit()

        except SQLAlchemyError as exc:
            session.rollback()
            raise SmartotumSyncException("Failed to synchronize Smartotum data") from exc
        except Exception as exc:
            session.rollback()
            raise SmartotumSyncException("Smartotum synchronization failed") from exc

        return
    
    @staticmethod
    def get_rules_from_smartotum(access_token: str, system_uuid: str) -> List[SmartotumRule]:

        client = SmartotumClient()

        return client.get_rules(access_token,system_uuid)
    
    @staticmethod
    def post_rules_to_smartotum(access_token: str, system_uuid: str, rules: List[SmartotumRule]) -> List[SmartotumRule]:

        client = SmartotumClient()

        return client.post_rules(access_token,system_uuid,rules)


    @staticmethod
    def update_database_smartotum_for_user(user: User):
        access_token = request.cookies.get("st_access_token")
        if not access_token:
            raise MissingJWTException("Smartotum access token missing")

        SmartotumService.update_database_smartotum(access_token, user)
