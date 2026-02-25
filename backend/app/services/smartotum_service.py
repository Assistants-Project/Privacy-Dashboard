from uuid import UUID

from flask import request
from sqlalchemy.exc import SQLAlchemyError

from ..exceptions import MissingJWTException, SmartotumSyncException
from ..integrations.smartotum import SmartotumClient
from ..repositories.application_repository import ApplicationRepository
from ..repositories.consent_repository import ConsentRepository
from ..repositories.room_repository import RoomRepository
from ..repositories.smart_home_repository import SmartHomeRepository
from ..models import Application
from ..models import Room
from ..models import User
from ..models import UserRole
from ..models import SmartHome
from ..models import Device
from ..repositories.device_repository import DeviceRepository
from ..repositories.user_repository import UserRepository
from ..exceptions.entities.room_exceptions import RoomNotFoundException
from ..extensions import db
from ..integrations.smartotum.client import SmartotumRule
from typing import List

class SmartotumService:

    @staticmethod
    def update_database_smartotum(access_token: str, user: User):
        #for now it doesn't update rules, waiting for a database implementation for rules by the PTP app
        session = db.session
        try:
            client = SmartotumClient()
            #get system list of the user
            systems_new = client.get_systems(access_token)
            
            from ..services.rule_service import RuleService
            rule_service = RuleService()

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
                        # Room used for devices that Smartotum does not assign to any room.
                        # Keep name stable and different from the home name to avoid UI duplicates.
                        name="Unassigned devices",
                        home_id=home.id,
                        category="Unassigned"
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
                
                    #if the device does not have a room we save it in a special room
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
                
                # regenerate home ontology with updated devices
                try:
                    from app.services.owl_service import OWLService
                    OWLService.create_home_ontology(str(system.home_uuid))
                except Exception as e:
                    print(f"Failed to regenerate ontology for home {system.home_uuid}: {e}")
                
                # sync rules
                try:
                     rules = client.get_rules(access_token, system.home_uuid)
                     # perform full sync (create, update, delete)
                     rule_service.sync_rules_for_home(home, rules, access_token)
                     
                     # cleanup rules with deleted devices
                     rule_service.cleanup_orphaned_rules(home, access_token)
                     
                     # update rule locations to match device locations
                     rule_service.update_rule_locations(home)
                except Exception as e:
                     print(f"Failed to sync rules for home {system.home_uuid}: {e}")

            existing_home: list[SmartHome] = SmartHomeRepository.get_homes_by_user_id(user.id)

            for home in existing_home:
                if home.uuid not in new_homes_uuid:
                    # The home might be shared with other users
                    # we remove only the relation and delete the home only if no ones shares it.
                    ApplicationRepository.update_applications_for_home(
                        user_id=user.id,
                        smart_home_id=home.id,
                        applications=[],
                    )
                    ConsentRepository.delete_user_smart_home_available_consents_by_ds_id_and_smart_home_id(
                        user_id=user.id,
                        smart_home_id=home.id,
                    )
                    SmartHomeRepository.unassign_home(home.id, user.id)
                    session.flush()

                    owners = SmartHomeRepository.get_home_owners_by_home_id(home.id)
                    if not owners:
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


    @staticmethod
    def update_installed_application_for_user(user: User):

        access_token = request.cookies.get("st_access_token")
        if not access_token:
            raise MissingJWTException("Smartotum access token missing")
        
        session = db.session

        try:
            client = SmartotumClient()

            systems_new = client.get_systems(access_token)

            def get_valid_data_controller(email: str, app_identifier: str) -> User:
                data_controller = UserRepository.get_user_by_email(email)
                if not data_controller:
                    raise SmartotumSyncException(
                        f"Data Controller with email {email} not found for application {app_identifier}."
                    )
                if data_controller.role != UserRole.DATA_CONTROLLER:
                    raise SmartotumSyncException(
                        f"User {email} is not a Data Controller for application {app_identifier}."
                    )
                return data_controller

            # for every home owned by the user
            for system in systems_new:

                # update installed applications for the home
                smartotum_applications = client.get_home_applications(
                    access_token, system.home_uuid
                )

                applications_payload: list[Application] = []
                data_controller_emails_by_app_id: dict[str, list[str]] = {}
                available_consents_by_app_id: dict[str, list[str]] = {}

                for smartotum_application in smartotum_applications:
                    app_id = smartotum_application.id
                    app_title = smartotum_application.name
                    data_controller_emails = smartotum_application.data_controllers_email or []
                    if len(data_controller_emails) == 0:
                        raise SmartotumSyncException(
                            f"Application {app_id} has no Data Controller owner."
                        )
                    owner_email = data_controller_emails[0]
                    owner_data_controller = get_valid_data_controller(owner_email, app_id)
                    applications_payload.append(
                        Application(
                            name=app_id,
                            title=app_title,
                            description=smartotum_application.description,
                            owner_user_id=owner_data_controller.id,
                        )
                    )
                    data_controller_emails_by_app_id[app_id] = (
                        data_controller_emails
                    )
                    available_consents_by_app_id[app_id] = (
                        smartotum_application.available_consents or []
                    )

                found_home = SmartHomeRepository.get_home_by_uuid(system.home_uuid)

                if found_home is None:
                    # If the home is not known locally we skip this system and continue with the others.
                    continue

                ApplicationRepository.update_applications_for_home(
                    user_id=user.id,
                    smart_home_id=found_home.id,
                    applications=applications_payload,
                )

                # link application to Data Controllers:
                # first email is the owner, the next ones are delegates.
                for app_id, data_controller_emails in data_controller_emails_by_app_id.items():
                    application = ApplicationRepository.get_application_by_name(app_id)
                    if not application:
                        continue

                    if len(data_controller_emails) == 0:
                        raise SmartotumSyncException(
                            f"Application {app_id} has no Data Controller owner."
                        )

                    owner_email = data_controller_emails[0]
                    owner_data_controller = get_valid_data_controller(owner_email, app_id)

                    if application.owner_user_id is None:
                        application.owner_user_id = owner_data_controller.id
                    elif application.owner_user_id != owner_data_controller.id:
                        raise SmartotumSyncException(
                            f"Owner mismatch for application {app_id}: "
                            f"current owner id={application.owner_user_id}, incoming owner={owner_email}."
                        )

                    ApplicationRepository.ensure_application_managed_by_user(
                        owner_data_controller.id, application.id
                    )

                    for delegate_email in data_controller_emails[1:]:
                        delegate_data_controller = get_valid_data_controller(
                            delegate_email, app_id
                        )
                        ApplicationRepository.ensure_application_managed_by_user(
                            delegate_data_controller.id, application.id
                        )

                # update available consents for application
                for app_id, available_consents in available_consents_by_app_id.items():
                    application = ApplicationRepository.get_application_by_name(app_id)

                    if not application:
                        continue

                    ConsentRepository.upsert_available_consents_for_application(
                        application.id, available_consents
                    )
                
            #committiamo una sola volta alla fine cosi se ci sono errori è facile fare il revert
            session.commit()

        except SQLAlchemyError as exc:
            session.rollback()
            raise SmartotumSyncException("Failed to synchronize Smartotum applications") from exc
        except Exception as exc:
            session.rollback()
            raise SmartotumSyncException("Smartotum applications synchronization failed") from exc
