from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from ...exceptions import (
    WrongUserCredentialsException,
    SmartotumServiceUnavailableException,
    SmartotumTimeoutException,
)
from requests import RequestException
from requests.exceptions import HTTPError, Timeout
from uuid import UUID
import requests
from flask import current_app
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import uuid

@dataclass
class SmartotumLoginResult:
    user: Dict[str, Any]
    access_token: str
    refresh_token: str
    front_token: Optional[str]

@dataclass
class SmartotumSmartHomeResult:
    home_uuid: str
    name: str
    address: str
    zip_code: str
    country: str


@dataclass
class SmartotumHomeRoomResult:
    room_uuid: UUID
    name: str
    category: str | None = None

@dataclass
class SmartotumApplicationResult:
    application_uuid: UUID
    id: str
    name: str
    description: str | None = None
    data_controllers_email: list[str] | None = None
    available_consents: list[str] | None = None
    # Optional mapping: consent content -> SIFIS action id (e.g., sifis_all_video_actions)
    available_consents_action_ids: Dict[str, str] | None = None

@dataclass
class SmartotumDeviceResult:
    device_uuid: UUID
    name: str
    topic_name: str
    room_uuid: UUID | None = None #se non hanno una casa per il momento lasciamo none

@dataclass
class SmartotumRule:
    rule_uuid: str
    rule_topic_name: str
    target_uuid: str
    target_topic_name: str
    time_start: str | None = None
    time_end: str | None = None
    days: list[str] | None = None
    expiration_date: str | None = None

class SmartotumClient:
    #initialize env variables
    def __init__(self, session: Optional[requests.Session] = None, session_retry: Optional[requests.Session] = None) -> None:
        cfg = current_app.config
        self._base_url = cfg["SMARTOTUM_BASE_URL"].rstrip("/")
        self._base_dht_url = cfg["SMARTOTUM_DHT_URL"].rstrip("/")
        self._api_base_path = cfg["SMARTOTUM_API_BASE_PATH"].strip("/")
        self._smartotum_device_topics = cfg["SMARTOTUM_DEVICE_TOPICS"]
        self._rule_topic = cfg["SMARTOTUM_RULE_TOPIC"]
        self._timeout = cfg.get("SMARTOTUM_TIMEOUT", 1)
        self._applications_file = cfg.get("SMARTOTUM_APPLICATIONS_JSON")
        self._is_testing = os.getenv("FLASK_ENV") == "testing"
        self._testing_data_root = Path(current_app.root_path).parent / "testing" / "data"

        self._session = session or requests.Session()

        if session_retry is None:

            self._session_retry = requests.Session()

            retry_strategy = Retry(
                total=4,
                status_forcelist=[429,500,502,503,504], 
                read=3,
                connect=3,
                backoff_factor=0.5,
                allowed_methods=frozenset({"GET", "POST"})
            )
        
            retry_adapter = HTTPAdapter(max_retries=retry_strategy)

            self._session_retry.mount("http://", retry_adapter)
            self._session_retry.mount("https://", retry_adapter)
        
        else:
            self._session_retry = session_retry 
        
        self._rid = cfg["SMARTOTUM_RID"]
        self._auth_mode = cfg["SMARTOTUM_AUTH_MODE"]

    #helper function that return the url to send api to
    def smartotum_api_url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"
    
    def smartotum_dht_api_url(self, path: str, home_uuid: str) -> str:
        base = self._base_dht_url.replace("house_name", home_uuid).rstrip("/")
        return f"{base}/{path.lstrip('/')}"

    def _handle_http_error(self, exc: HTTPError) -> None:
        resp = getattr(exc, "response", None)
        status = getattr(resp, "status_code", None)
        url = getattr(resp, "url", None)
        if status in (401, 403):
            raise WrongUserCredentialsException("Smartotum access token invalid or expired") from exc
        if status is not None:
            raise SmartotumServiceUnavailableException(
                f"Smartotum request failed with HTTP {status}" + (f" ({url})" if url else "")
            ) from exc
        raise SmartotumServiceUnavailableException("Smartotum request failed") from exc
    
    def _build_rule_payload(self, rule: SmartotumRule) -> Dict[str, Any]:

        value: Dict[str, Any] = {
            "target_topic": rule.target_topic_name,
            "target_uuid": str(rule.target_uuid),
        }
        
        if rule.time_start:
            value["time_start"] = rule.time_start
        if rule.time_end:
            value["time_end"] = rule.time_end
        if rule.days:
            value["days"] = [str(day) for day in rule.days]
        if rule.expiration_date:
            value["expiration_date"] = rule.expiration_date

        return {
            "topic_uuid": str(rule.rule_uuid),
            "topic_name": rule.rule_topic_name,
            "value": value,
        }
    
    def post_rules(self, access_token: str, system_uuid: str, rules: List[SmartotumRule]) -> List[SmartotumRule]:
        if self._is_testing:
            return self._post_rules_testing(system_uuid, rules)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if not rules:
            return []

        created_rules: List[SmartotumRule] = []

        for rule in rules:

            # Smartotum DHT write API (per prof):
            # POST /.dht/topic_name/<topic>/topic_uuid/<uuid> with BODY = JSON stored in the "value" field.
            wrapper_payload = self._build_rule_payload(rule)
            value_payload = wrapper_payload.get("value", {}) or {}
            complete_url = self.smartotum_dht_api_url(
                f"/topic_name/{self._rule_topic}/topic_uuid/{rule.rule_uuid}",
                system_uuid,
            )

            try:
                current_app.logger.info(
                    "Smartotum post_rules: home_uuid=%s topic=%s topic_uuid=%s url=%s value=%s",
                    str(system_uuid),
                    str(self._rule_topic),
                    str(rule.rule_uuid),
                    str(complete_url),
                    value_payload,
                )
                response = self._session.post(
                    complete_url, headers=headers, json=value_payload, timeout=self._timeout
                )
                response.raise_for_status()
            except Timeout as exc:
                raise SmartotumTimeoutException("Smartotum request timed out") from exc
            except HTTPError as exc:
                resp = getattr(exc, "response", None)
                current_app.logger.error(
                    "Smartotum post_rules failed: status=%s url=%s payload=%s response=%s",
                    getattr(resp, "status_code", None),
                    getattr(resp, "url", complete_url),
                    value_payload,
                    (getattr(resp, "text", "") or "")[:500],
                )
                self._handle_http_error(exc)
            except RequestException as exc:
                raise SmartotumServiceUnavailableException("Smartotum request failed") from exc
            
            created_rules.append(rule)

        return created_rules


    def get_rules(self, access_token: str, system_uuid: str) -> List[SmartotumRule]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        rules: List[SmartotumRule] = []

        if self._is_testing:
            rules_response: List[Dict[str, Any]] = self._get_testing_rules_state(system_uuid)
        else:
            complete_url=self.smartotum_dht_api_url(f"/topic_name/{self._rule_topic}", system_uuid)

            try:
                response = self._session_retry.get(
                    complete_url, headers=headers, timeout=self._timeout
                )
                response.raise_for_status()
            except Timeout as exc:
                raise SmartotumTimeoutException("Smartotum request timed out") from exc
            except HTTPError as exc:
                self._handle_http_error(exc)
            except RequestException as exc:
                raise SmartotumServiceUnavailableException("Smartotum request failed") from exc
                
            rules_response: List[Dict[str,Any]] = response.json()

        for rule_response in rules_response:

            rule_uuid = rule_response.get("topic_uuid")
            value = rule_response.get("value", {}) or {}
            target_uuid = value.get("target_uuid")
            target_topic = value.get("target_topic")
            days_value = value.get("days", [])
            days = [str(day) for day in days_value]

            #TODO: Evaluate if there is a need for more validation because our app is responsable to create and receive correct rules

            rules.append(
                SmartotumRule(
                    rule_uuid=str(rule_uuid),
                    rule_topic_name=self._rule_topic,
                    target_uuid=str(target_uuid),
                    target_topic_name=str(target_topic),
                    time_start=value.get("time_start"),
                    time_end=value.get("time_end"),
                    days=days,
                    expiration_date=value.get("expiration_date"),
                )
            )


        return rules

#return a topic directly from the dht
#in testing reads from backend/testing/data/dht/<home_uuid>
#in dev or demo talks to the official smartotum dht
    def get_dht_topic_items(self, access_token: str, system_uuid: str, topic_name: str) -> List[Dict[str, Any]]:
        if self._is_testing:
            if topic_name == self._rule_topic:
                return self._get_testing_rules_state(system_uuid)
            return self._get_testing_topic_items(system_uuid, topic_name)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        complete_url = self.smartotum_dht_api_url(f"/topic_name/{topic_name}", system_uuid)
        try:
            response = self._session_retry.get(
                complete_url, headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
        except Timeout as exc:
            raise SmartotumTimeoutException("Smartotum request timed out") from exc
        except HTTPError as exc:
            self._handle_http_error(exc)
        except RequestException as exc:
            raise SmartotumServiceUnavailableException("Smartotum request failed") from exc

        items = response.json()
        return items if isinstance(items, list) else []

#return all the dht of a given home from smartotum or from file if in testing mode
    def get_dht_all_items(self, access_token: str, system_uuid: str) -> List[Dict[str, Any]]:
        if self._is_testing:
            return self._get_testing_all_items(system_uuid)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        complete_url = self.smartotum_dht_api_url("/get_all", system_uuid)
        try:
            response = self._session_retry.get(
                complete_url, headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
        except Timeout as exc:
            raise SmartotumTimeoutException("Smartotum request timed out") from exc
        except HTTPError as exc:
            self._handle_http_error(exc)
        except RequestException as exc:
            raise SmartotumServiceUnavailableException("Smartotum request failed") from exc

        items = response.json()
        return items if isinstance(items, list) else []

    def delete_rule(self, access_token: str, system_uuid: str, rule_uuid: str) -> bool:
        if self._is_testing:
            return self._delete_rule_testing(system_uuid, rule_uuid)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        complete_url = self.smartotum_dht_api_url(
            f"/topic_name/{self._rule_topic}/topic_uuid/{rule_uuid}", system_uuid
        )
        try:
            response = self._session.delete(
                complete_url, headers=headers, timeout=self._timeout
            )
            # Idempotent delete: if already missing, treat as success.
            if response.status_code == 404:
                return True
            response.raise_for_status()
        except Timeout as exc:
            raise SmartotumTimeoutException("Smartotum request timed out") from exc
        except HTTPError as exc:
            self._handle_http_error(exc)
        except RequestException as exc:
            raise SmartotumServiceUnavailableException("Smartotum request failed") from exc
        return response.status_code in (200, 204)

    def get_home_devices(self, access_token: str, system_uuid: str) -> List[SmartotumDeviceResult]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        devices: List[SmartotumDeviceResult] = []

        for topic_name in self._smartotum_device_topics:
            if self._is_testing:
                items = self._get_testing_topic_items(system_uuid, topic_name)
            else:
                complete_url=self.smartotum_dht_api_url(f"/topic_name/{topic_name}", system_uuid)

                try:
                    response = self._session_retry.get(
                        complete_url, headers=headers, timeout=self._timeout
                    )
                    response.raise_for_status()
                except Timeout as exc:
                    raise SmartotumTimeoutException("Smartotum request timed out") from exc
                except HTTPError as exc:
                    self._handle_http_error(exc)
                except RequestException as exc:
                    raise SmartotumServiceUnavailableException("Smartotum request failed") from exc
                
                items: List[Dict[str,Any]] = response.json()

            for item in items:
                value = item.get("value", {})
                device_uuid = item.get("topic_uuid")
                name = value.get("name")
                area_name = value.get("area_name")
                topic_name = topic_name

                device = SmartotumDeviceResult(
                    device_uuid=UUID(device_uuid),
                    name=str(name) if name is not None else "",
                    room_uuid=UUID(area_name) if area_name is not None else None,
                    topic_name = topic_name
                )

                devices.append(device)

            
        return devices

    
    def get_home_rooms(self, access_token: str, system_uuid: str) -> List[SmartotumHomeRoomResult]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        if self._is_testing:
            items = self._get_testing_topic_items(system_uuid, "domo_room")
        else:
            complete_url=self.smartotum_dht_api_url(f"/topic_name/domo_room", system_uuid)

            try:
                response = self._session_retry.get(
                    complete_url, headers=headers, timeout=self._timeout
                )
                response.raise_for_status()
            except Timeout as exc:
                raise SmartotumTimeoutException("Smartotum request timed out") from exc
            except HTTPError as exc:
                self._handle_http_error(exc)
            except RequestException as exc:
                raise SmartotumServiceUnavailableException("Smartotum request failed") from exc

            items: List[Dict[str, Any]] = response.json()
        rooms: List[SmartotumHomeRoomResult] = []

        for item in items:
            topic_uuid = UUID(item.get("topic_uuid"))
            value = item.get("value", {})
            name = value.get("name")
            category = value.get("category")
            rooms.append(
                SmartotumHomeRoomResult(
                    room_uuid=topic_uuid,
                    name=str(name),
                    category=str(category) if category is not None else None,
                )
            )

        return rooms
    
    def get_home_applications(self, access_token: str, system_uuid: str) -> List[SmartotumApplicationResult]:

        if self._applications_file:

            path = Path(str(self._applications_file))

            #supports both absolute and relative path from the backend folder
            if not path.is_absolute():
                if not path.exists():
                    backend_root = Path(current_app.root_path).parent
                    path = backend_root / path
                path = path.resolve()

            with path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)

            if not isinstance(payload, list):
                raise ValueError("SMARTOTUM_APPLICATIONS_JSON must be an array")

            applications: List[SmartotumApplicationResult] = []

            for i,item in enumerate(payload):
                if not isinstance(item, dict):
                    raise ValueError(f"apps[{i}] must be an object")

                application_id = item.get("id")
                if not isinstance(application_id, str) or not application_id.strip():
                    raise ValueError(f"apps[{i}].id is required and must not be empty")
                normalized_application_id = application_id.strip()

                name = item.get("name")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError(f"apps[{i}].name is required and must not be empty")
                normalized_name = name.strip()

                description = item.get("description")
                if description is not None and not isinstance(description, str):
                    raise ValueError(f"apps[{i}].description must be a string or null")
                normalized_description = description.strip() if isinstance(description, str) else None
                if normalized_description == "":
                    normalized_description = None
                
                data_controllers_email = item.get("data_controllers_email", [])
                # deve essere un array di stringhe
                if not isinstance(data_controllers_email, list):
                    raise ValueError(f"apps[{i}].data_controllers_email must be an array of strings")
                
                # per ciascuna email controlliamo tipo e normalizziamo spazi
                normalized_data_controllers_email: list[str] = []
                for email in data_controllers_email:
                    if not isinstance(email, str):
                        raise ValueError(f"apps[{i}].data_controllers_email must contain only strings")
                    
                    normalized_email = email.strip()
                    if normalized_email == "":
                        continue
                    normalized_data_controllers_email.append(normalized_email)

                available_consents = item.get("available_consents", [])
                if not isinstance(available_consents, list):
                    raise ValueError(f"apps[{i}].available_consents must be an array of objects")

                normalized_available_consents: list[str] = []
                available_consents_action_ids: Dict[str, str] = {}
                for j, consent in enumerate(available_consents):
                    if not isinstance(consent, dict):
                        raise ValueError(f"apps[{i}].available_consents[{j}] must be an object")

                    content = consent.get("content")
                    if not isinstance(content, str) or not content.strip():
                        raise ValueError(f"apps[{i}].available_consents[{j}].content is required and must not be empty")
                    normalized_content = content.strip()
                    normalized_available_consents.append(normalized_content)

                    sifis_action_id = consent.get("sifis_action_id")
                    if sifis_action_id is not None:
                        if not isinstance(sifis_action_id, str):
                            raise ValueError(f"apps[{i}].available_consents[{j}].sifis_action_id must be a string or null")
                        normalized_action_id = sifis_action_id.strip()
                        if normalized_action_id and normalized_content not in available_consents_action_ids:
                            available_consents_action_ids[normalized_content] = normalized_action_id

                # creiamo l'oggetto applicazione finale già normalizzato
                unique_available_consents = list(dict.fromkeys(normalized_available_consents))
                applications.append(
                    SmartotumApplicationResult(
                        application_uuid = UUID(str(uuid.uuid4())),
                        id=normalized_application_id,
                        name=normalized_name,
                        description=normalized_description,
                        data_controllers_email=list(dict.fromkeys(normalized_data_controllers_email)),
                        available_consents=unique_available_consents,
                        available_consents_action_ids=available_consents_action_ids or None,
                    )
                )

            return applications
       

        # Fallback to Smartotum api when the mock is not enabled
        # for now we don't know how is done so we guess

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        complete_url=self.smartotum_dht_api_url(f"/topic_name/domo_app", system_uuid)

        try:
            response = self._session_retry.get(
                complete_url, headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
        except RequestException as exc:
            raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc

        items: List[Dict[str, Any]] = response.json()
        applications: List[SmartotumApplicationResult] = []


        for item in items:
            #we assume that the topic_uuid is a vaid UUID
            topic_uuid = UUID(item.get("topic_uuid"))
            value = item.get("value", {})
            name = value.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            application_id = value.get("id")
            if not isinstance(application_id, str) or not application_id.strip():
                application_id = name.strip()
            else:
                application_id = application_id.strip()
            description = None

            applications.append(
                SmartotumApplicationResult(
                    application_uuid=topic_uuid,
                    id=application_id,
                    name=name.strip(),
                    description=description,
                    data_controllers_email=[],
                    available_consents=[],
                    available_consents_action_ids=None,
                )
            )

        return applications

    

    def login(self, email:str, password: str) -> SmartotumLoginResult:
        if self._is_testing:
            return self._get_testing_login_result(email)

        #payload to send to smartotum login system
        payload = {
            "formFields": [
                {"id": "email", "value": email},
                {"id": "password", "value": password},
            ]
        }

        #headers to send with payload
        headers = {
            "Rid": self._rid,
            "St-Auth-mode": self._auth_mode,
            "Content-Type": "application/json",
        }


        try:
            response = self._session_retry.post(
                self.smartotum_api_url(f"{self._api_base_path}/signin"),
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except Timeout as exc:
            raise SmartotumTimeoutException("Smartotum login timed out") from exc
        except RequestException as exc:
            raise SmartotumServiceUnavailableException("Smartotum service unavailable") from exc
    
        #think if it's needed a try except also here if smartotum doesn't respond with a json
        data = response.json()
        
        if data.get("status") == "WRONG_CREDENTIALS_ERROR" or "user" not in data:
            raise WrongUserCredentialsException("Invalid email or password!")
        
        access_token = response.headers.get("st-access-token")
        refresh_token = response.headers.get("st-refresh-token")

        if not access_token or not refresh_token:
            raise SmartotumServiceUnavailableException("missing tokens from login response Smartotum")
        
        return SmartotumLoginResult(
            user=data.get("user", {}),
            access_token=access_token,
            refresh_token=refresh_token,
            front_token=response.headers.get("front-token"),
        )
    
    def get_systems(self, access_token: str) -> List[SmartotumSmartHomeResult]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        if self._is_testing:
            payload = self._get_testing_systems_payload()
        else:
            params = {
                "offset": 0,
                "limit": 100,
            }

            try:
                response = self._session_retry.get(
                    self.smartotum_api_url("service/systems"), headers=headers, params=params, timeout=self._timeout
                )
                response.raise_for_status()
            except RequestException as exc:
                raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc
            
            payload = response.json()
        data = payload.get("data", [])

        homes: List[SmartotumSmartHomeResult] = []

        for item in data:
            home_uuid = item.get("id")
            name = item.get("name")
            address = item.get("address")
            zip_code = item.get("zip_code")
            country = item.get("country")


            homes.append(
                SmartotumSmartHomeResult(
                    home_uuid=home_uuid,
                    name=str(name),
                    address=str(address),
                    zip_code=str(zip_code),
                    country=str(country),
                )
            )

        return homes

    def _post_rules_testing(self, system_uuid: str, rules: List[SmartotumRule]) -> List[SmartotumRule]:
        created_rules: List[SmartotumRule] = []
        rules_state = self._get_testing_rules_state(system_uuid)

        for rule in rules:
            payload = self._build_rule_payload(rule)
            entry = {
                "topic_name": self._rule_topic,
                "topic_uuid": str(rule.rule_uuid),
                "value": payload.get("value", {}),
            }

            updated = False
            for i, item in enumerate(rules_state):
                if item.get("topic_uuid") == str(rule.rule_uuid):
                    rules_state[i] = entry
                    updated = True
                    break

            if not updated:
                rules_state.append(entry)

            created_rules.append(rule)

        self._write_testing_rules_state(system_uuid, rules_state)
        return created_rules

    def _get_testing_rules_state(self, system_uuid: str) -> List[Dict[str, Any]]:
        rules_file = self._get_testing_rules_read_path(system_uuid)
        return self._read_testing_list_file(rules_file)

    def _delete_rule_testing(self, system_uuid: str, rule_uuid: str) -> bool:
        rules_state = self._get_testing_rules_state(system_uuid)
        next_rules_state = [item for item in rules_state if item.get("topic_uuid") != str(rule_uuid)]
        self._write_testing_rules_state(system_uuid, next_rules_state)
        return True

    def _get_testing_topic_items(self, system_uuid: str, topic_name: str) -> List[Dict[str, Any]]:
        topic_file = self._testing_data_root / "dht" / str(system_uuid) / f"{topic_name}.json"
        return self._read_testing_list_file(topic_file)

    def _get_testing_all_items(self, system_uuid: str) -> List[Dict[str, Any]]:
        home_dir = self._testing_data_root / "dht" / str(system_uuid)
        items: List[Dict[str, Any]] = []
        included_rules = False

        if home_dir.exists() and home_dir.is_dir():
            for p in sorted(home_dir.glob("*.json")):
                topic_name = p.stem
                if topic_name == f"{self._rule_topic}_output":
                    continue
                if topic_name == self._rule_topic:
                    items.extend(self._get_testing_rules_state(system_uuid))
                    included_rules = True
                else:
                    items.extend(self._read_testing_list_file(p))

        # In case a test bootstraps rules state without a fixture file.
        if not included_rules:
            rules = self._get_testing_rules_state(system_uuid)
            if rules:
                items.extend(rules)

        return items

    def _get_testing_login_result(self, email: str) -> SmartotumLoginResult:
        return SmartotumLoginResult(
            user={"email": email},
            access_token="mock-smartotum-access-token",
            refresh_token="mock-smartotum-refresh-token",
            front_token="mock-front-token",
        )

    def _get_testing_systems_payload(self) -> Dict[str, Any]:
        systems_file = self._testing_data_root / "systems.json"
        if not systems_file.exists():
            return {"data": [], "offset": 0, "limit": 100}
        try:
            payload = json.loads(systems_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"data": [], "offset": 0, "limit": 100}
        return payload if isinstance(payload, dict) else {"data": [], "offset": 0, "limit": 100}

    def _get_testing_rules_fixture_path(self, system_uuid: str) -> Path:
        return self._testing_data_root / "dht" / str(system_uuid) / f"{self._rule_topic}.json"

    def _get_testing_rules_output_path(self, system_uuid: str) -> Path:
        return self._testing_data_root / "dht" / str(system_uuid) / f"{self._rule_topic}_output.json"

    def _get_testing_rules_read_path(self, system_uuid: str) -> Path:
        fixture_path = self._get_testing_rules_fixture_path(system_uuid)
        output_path = self._get_testing_rules_output_path(system_uuid)

        if not output_path.exists():
            return fixture_path
        if not fixture_path.exists():
            return output_path

        try:
            fixture_mtime = fixture_path.stat().st_mtime
            output_mtime = output_path.stat().st_mtime
        except OSError:
            return output_path

        # In testing usiamo il file modificato più di recente come source of truth:
        # così per la demo si può aggiornare manualmente il fixture e farlo "vincere"
        # senza dover cancellare ogni volta il file di output generato dal sistema.
        return fixture_path if fixture_mtime > output_mtime else output_path

    def _write_testing_rules_state(self, system_uuid: str, rules_state: List[Dict[str, Any]]) -> None:
        output_path = self._get_testing_rules_output_path(system_uuid)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(rules_state, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    def _read_testing_list_file(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        return payload if isinstance(payload, list) else []
