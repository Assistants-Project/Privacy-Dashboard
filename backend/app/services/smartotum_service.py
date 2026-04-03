import json
from uuid import UUID

from flask import current_app, request
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
from typing import Any, List
from ..services.consent_policy_rule_service import ConsentPolicyRuleService

class SmartotumService:

    @staticmethod
    def update_database_smartotum(access_token: str,user: User,target_home_uuid: str | None = None,prune_missing_homes: bool = True):
        #for now it doesn't update rules, waiting for a database implementation for rules by the PTP app
        session = db.session
        try:
            client = SmartotumClient()
            #get system list of the user
            systems_new = client.get_systems(access_token)

            #to force update of only a home
            if target_home_uuid is not None:
                systems_new = [
                    system for system in systems_new if system.home_uuid == target_home_uuid
                ]
            
            from ..services.rule_service import RuleService
            rule_service = RuleService()

            new_homes_uuid = set()

            #for ever home owned by the user
            for system in systems_new:
                new_homes_uuid.add(system.home_uuid)
                #insert or update the home
                home = SmartHomeRepository.upsert_home(system.home_uuid,system.name,system.address,system.zip_code,system.country)
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

            if prune_missing_homes and target_home_uuid is None:
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
        warnings: list[str] = []

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

            def append_warning(message: str) -> None:
                warnings.append(message)

            def append_skipped_application_warning(app_identifier: str) -> None:
                warnings.append(
                    f"Application {app_identifier} could not be synchronized because no valid Data Controller is registered in the dashboard. The application was skipped."
                )

            def log_sync_issue(message: str) -> None:
                current_app.logger.warning("Smartotum applications refresh for %s: %s", user.email, message)

            def get_action_id_from_rule_url(url: str | None) -> str | None:
                if not url:
                    return None
                if "#" in url:
                    return url.split("#")[-1]
                return url

            smartotum_rules_by_home_uuid: dict[str, list[SmartotumRule]] = {}

            def get_home_rules(home_uuid: str) -> list[SmartotumRule]:
                cached_rules = smartotum_rules_by_home_uuid.get(home_uuid)
                if cached_rules is not None:
                    return cached_rules
                cached_rules = client.get_rules(access_token, home_uuid)
                smartotum_rules_by_home_uuid[home_uuid] = cached_rules
                return cached_rules

            def sync_consent_policy_rule(available_consent: Any, given_at: Any, smart_home: SmartHome, subject_email: str) -> None:
                desired_action_id = getattr(available_consent, "sifis_action_id", None)
                base_rule_uuid = cps.consent_rule_uuid(
                    home_uuid=str(smart_home.uuid),
                    consent_uuid=available_consent.uuid,
                )
                existing_rule = cps._rule_service.rule_repo.get_rule_by_uuid(base_rule_uuid)
                existing_action_url = None
                if existing_rule and getattr(existing_rule, "actions", None):
                    try:
                        existing_action_url = existing_rule.actions[0].url
                    except Exception:
                        existing_action_url = None
                existing_action_id = get_action_id_from_rule_url(existing_action_url)

                # If consent is given OR mapping is missing, make sure consent rule is not present.
                if given_at is not None or not desired_action_id:
                    if existing_rule:
                        action_id_for_delete = desired_action_id or existing_action_id
                        if not action_id_for_delete:
                            raise SmartotumSyncException(
                                f"Cannot cleanup consent rule for consent {available_consent.uuid}: missing action id"
                            )
                        cps.delete_consent_deny_rule(
                            smart_home=smart_home,
                            consent_uuid=available_consent.uuid,
                            sifis_action_id=action_id_for_delete,
                            access_token=access_token,
                        )
                    return

                # Consent not given and mapping exists: ensure rule exists and matches the desired action.
                if existing_rule:
                    if existing_action_id != desired_action_id:
                        action_id_for_delete = existing_action_id or desired_action_id
                        cps.delete_consent_deny_rule(
                            smart_home=smart_home,
                            consent_uuid=available_consent.uuid,
                            sifis_action_id=action_id_for_delete,
                            access_token=access_token,
                        )
                        cps.create_consent_deny_rule(
                            smart_home=smart_home,
                            subject_email=subject_email,
                            consent_uuid=available_consent.uuid,
                            sifis_action_id=desired_action_id,
                            access_token=access_token,
                        )
                    return

                try:
                    restored = cps.restore_local_consent_deny_rule_without_publish(
                        smart_home=smart_home,
                        subject_email=subject_email,
                        consent_uuid=available_consent.uuid,
                        sifis_action_id=desired_action_id,
                        smartotum_rules=get_home_rules(str(smart_home.uuid)),
                    )
                except Exception as exc:
                    raise SmartotumSyncException(
                        f"Cannot restore consent rule for consent {available_consent.uuid}: {exc}"
                    ) from exc

                if restored:
                    return

                cps.create_consent_deny_rule(
                    smart_home=smart_home,
                    subject_email=subject_email,
                    consent_uuid=available_consent.uuid,
                    sifis_action_id=desired_action_id,
                    access_token=access_token,
                )

            cps = ConsentPolicyRuleService()

            # Application sync depends on the local home snapshot.
            # If a home is missing locally, refresh only that home without pruning the others.
            for system in systems_new:
                found_home = SmartHomeRepository.get_home_by_uuid(system.home_uuid)
                if found_home is not None:
                    continue

                SmartotumService.update_database_smartotum(access_token,user,target_home_uuid=system.home_uuid,prune_missing_homes=False)

            # for every home owned by the user
            for system in systems_new:

                # update installed applications for the home
                try:
                    smartotum_applications = client.get_home_applications(
                        access_token, system.home_uuid
                    )
                except json.JSONDecodeError as exc:
                    raise SmartotumSyncException(
                        f"Smartotum applications synchronization failed: invalid applications configuration for home {system.home_uuid}"
                    ) from exc

                applications_payload: list[Application] = []
                data_controller_emails_by_app_id: dict[str, list[str]] = {}
                available_consents_by_app_id: dict[str, list[str]] = {}
                available_consents_action_ids_by_app_id: dict[str, dict[str, str]] = {}
                app_is_new_by_id: dict[str, bool] = {}

                for smartotum_application in smartotum_applications:
                    app_id = smartotum_application.id
                    app_title = smartotum_application.name
                    data_controller_emails = smartotum_application.data_controllers_email or []
                    app_is_new_by_id[app_id] = (
                        ApplicationRepository.get_application_by_name(app_id) is None
                    )
                    if len(data_controller_emails) == 0:
                        append_skipped_application_warning(app_id)
                        log_sync_issue(f"Application {app_id} has no Data Controller owner in Smartotum payload.")
                        continue
                    owner_email = data_controller_emails[0]
                    try:
                        owner_data_controller = get_valid_data_controller(owner_email, app_id)
                    except SmartotumSyncException as exc:
                        if app_is_new_by_id[app_id]:
                            append_skipped_application_warning(app_id)
                            log_sync_issue(exc.message)
                            continue
                        owner_data_controller = None
                        log_sync_issue(f"{exc.message} Existing application {app_id} kept its local owner and managers.")
                    applications_payload.append(
                        Application(
                            name=app_id,
                            title=app_title,
                            description=smartotum_application.description,
                            owner_user_id=owner_data_controller.id if owner_data_controller is not None else None,
                        )
                    )
                    if owner_data_controller is not None:
                        data_controller_emails_by_app_id[app_id] = (
                            data_controller_emails
                        )
                    available_consents_by_app_id[app_id] = (
                        smartotum_application.available_consents or []
                    )
                    available_consents_action_ids_by_app_id[app_id] = (
                        smartotum_application.available_consents_action_ids or {}
                    )

                found_home = SmartHomeRepository.get_home_by_uuid(system.home_uuid)

                if found_home is None:
                    # The targeted home refresh should have created the local home snapshot.
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

                    owner_email = data_controller_emails[0]
                    try:
                        owner_data_controller = get_valid_data_controller(owner_email, app_id)
                    except SmartotumSyncException as exc:
                        log_sync_issue(f"{exc.message} Existing application {app_id} kept its local owner and managers.")
                        continue

                    if application.owner_user_id is None:
                        application.owner_user_id = owner_data_controller.id
                    elif application.owner_user_id != owner_data_controller.id:
                        log_sync_issue(
                            f"Owner mismatch for application {app_id}: "
                            f"current owner id={application.owner_user_id}, incoming owner={owner_email}. "
                            f"Keeping current owner and skipping remote manager update."
                        )
                        continue

                    ApplicationRepository.ensure_application_managed_by_user(
                        owner_data_controller.id, application.id
                    )

                    if not app_is_new_by_id.get(app_id, False):
                        continue

                    for delegate_email in data_controller_emails[1:]:
                        try:
                            delegate_data_controller = get_valid_data_controller(
                                delegate_email, app_id
                            )
                        except SmartotumSyncException as exc:
                            log_sync_issue(f"{exc.message} Delegate was skipped for application {app_id}.")
                            continue
                        ApplicationRepository.ensure_application_managed_by_user(
                            delegate_data_controller.id, application.id
                        )

                # update available consents for application
                for app_id, available_consents in available_consents_by_app_id.items():
                    application = ApplicationRepository.get_application_by_name(app_id)

                    if not application:
                        continue

                    desired_available_consents = list(available_consents)
                    desired_action_ids_by_content = dict(
                        available_consents_action_ids_by_app_id.get(app_id, {})
                    )
                    desired_available_consents_set = set(desired_available_consents)
                    removed_available_consents = [
                        available_consent
                        for available_consent in list(application.available_consents)
                        if available_consent.content not in desired_available_consents_set
                    ]

                    if removed_available_consents:
                        installed_relations = (
                            ApplicationRepository.get_user_smart_home_applications_by_ds_id_and_application_id(
                                user.id, application.id
                            )
                        )

                        for removed_available_consent in removed_available_consents:
                            should_keep_removed_consent = False

                            for relation in installed_relations:
                                smart_home = relation.smart_home
                                if smart_home is None:
                                    continue

                                base_rule_uuid = cps.consent_rule_uuid(
                                    home_uuid=str(smart_home.uuid),
                                    consent_uuid=removed_available_consent.uuid,
                                )
                                existing_rule = (
                                    cps._rule_service.rule_repo.get_rule_by_uuid(
                                        base_rule_uuid
                                    )
                                )
                                if existing_rule is None:
                                    continue

                                action_id_for_delete = getattr(
                                    removed_available_consent, "sifis_action_id", None
                                )
                                if not action_id_for_delete:
                                    existing_action_url = None
                                    if getattr(existing_rule, "actions", None):
                                        try:
                                            existing_action_url = (
                                                existing_rule.actions[0].url
                                            )
                                        except Exception:
                                            existing_action_url = None
                                    action_id_for_delete = get_action_id_from_rule_url(
                                        existing_action_url
                                    )

                                if not action_id_for_delete:
                                    should_keep_removed_consent = True
                                    message = (
                                        f"Application {app_id} kept removed consent "
                                        f"'{removed_available_consent.content}' because a DHT cleanup "
                                        f"rule exists in home {smart_home.uuid} but no action id is available."
                                    )
                                    append_warning(message)
                                    log_sync_issue(message)
                                    break

                                try:
                                    cps.delete_consent_deny_rule(
                                        smart_home=smart_home,
                                        consent_uuid=removed_available_consent.uuid,
                                        sifis_action_id=action_id_for_delete,
                                        access_token=access_token,
                                    )
                                except Exception as exc:
                                    should_keep_removed_consent = True
                                    message = (
                                        f"Application {app_id} kept removed consent "
                                        f"'{removed_available_consent.content}' because DHT cleanup failed "
                                        f"for home {smart_home.uuid}: {exc}"
                                    )
                                    append_warning(message)
                                    log_sync_issue(message)
                                    break

                            if should_keep_removed_consent:
                                desired_available_consents.append(
                                    removed_available_consent.content
                                )
                                desired_available_consents_set.add(
                                    removed_available_consent.content
                                )
                                existing_action_id = getattr(
                                    removed_available_consent, "sifis_action_id", None
                                )
                                if existing_action_id:
                                    desired_action_ids_by_content[
                                        removed_available_consent.content
                                    ] = existing_action_id

                    ConsentRepository.upsert_available_consents_for_application(
                        application.id,
                        desired_available_consents,
                        desired_action_ids_by_content,
                        prune_missing=True,
                    )

                    # Default: if a consent is not given, enforce a deny rule immediately.
                    # This keeps Smartotum behavior aligned with the UI unchecked consents from the start
                    consent_rows = ConsentRepository.get_available_consents_with_given_state_by_ds_id_and_smart_home_id_and_application_id(
                        user.id, found_home.id, application.id
                    )
                    for available_consent, given_at in consent_rows:
                        sync_consent_policy_rule(
                            available_consent,
                            given_at,
                            found_home,
                            user.email,
                        )
                
            #commit at the end to revert easily
            session.commit()
            return {
                "message": "Apps updated from Smartotum installed apps of " + user.email,
                "warnings": warnings,
            }

        except SQLAlchemyError as exc:
            session.rollback()
            raise SmartotumSyncException("Failed to synchronize Smartotum applications") from exc
        except SmartotumSyncException:
            session.rollback()
            raise
        except Exception as exc:
            session.rollback()
            raise SmartotumSyncException("Smartotum applications synchronization failed") from exc
