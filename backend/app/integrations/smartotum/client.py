from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from ...exceptions import (
    WrongUserCredentialsException,
    SmartotumServiceUnavailableException,
    SmartotumTimeoutException,
)
from requests import RequestException
from requests.exceptions import Timeout
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
    name: str
    description: str | None = None
    data_controller_email: str | None = None

@dataclass
class SmartotumDeviceResult:
    device_uuid: UUID
    name: str
    topic_name: str
    room_uuid: UUID | None = None #se non hanno una casa per il momento lasciamo none

@dataclass
class SmartotumRule:
    rule_uuid: UUID
    rule_topic_name: str
    target_uuid: UUID
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
        base = self._base_dht_url.replace("house_name", home_uuid)
        return f"{base}/{path.lstrip('/')}"
    
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

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        complete_url = self.smartotum_dht_api_url(f"/topic_name/{self._rule_topic}", system_uuid)

        if not rules:
            return []

        created_rules: List[SmartotumRule] = []

        for rule in rules:

            payload = self._build_rule_payload(rule)

            try:
                response = self._session.post(
                    complete_url, headers=headers, json=payload, timeout=self._timeout
                )
                response.raise_for_status()
            except RequestException as exc:
                raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc
            
            created_rules.append(rule)

        return created_rules


    def get_rules(self, access_token: str, system_uuid: str) -> List[SmartotumRule]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        rules: List[SmartotumRule] = []

        complete_url=self.smartotum_dht_api_url(f"/topic_name/{self._rule_topic}", system_uuid)

        try:
            response = self._session_retry.get(
                complete_url, headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
        except RequestException as exc:
            raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc
            
        rules_response: List[Dict[str,Any]] = response.json()

        for rule_response in rules_response:

            rule_uuid = UUID(rule_response.get("topic_uuid"))


            value = rule_response.get("value", {}) or {}
            target_uuid = UUID(value.get("target_uuid"))
            target_topic = value.get("target_topic")
            days_value = value.get("days", [])
            days = [str(day) for day in days_value]

            #TODO: Evaluate if there is a need for more validation because our app is responsable to create and receive correct rules

            rules.append(
                SmartotumRule(
                    rule_uuid=rule_uuid,
                    rule_topic_name=self._rule_topic,
                    target_uuid=target_uuid,
                    target_topic_name=str(target_topic),
                    time_start=value.get("TIME_START"),
                    time_end=value.get("TIME_END"),
                    days=days,
                    expiration_date=value.get("EXPIRATION_DATE"),
                )
            )


        return rules

    def get_home_devices(self, access_token: str, system_uuid: str) -> List[SmartotumDeviceResult]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        devices: List[SmartotumDeviceResult] = []

        for topic_name in self._smartotum_device_topics:

            complete_url=self.smartotum_dht_api_url(f"/topic_name/{topic_name}", system_uuid)

            try:
                response = self._session_retry.get(
                    complete_url, headers=headers, timeout=self._timeout
                )
                response.raise_for_status()
            except RequestException as exc:
                raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc
            
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

        complete_url=self.smartotum_dht_api_url(f"/topic_name/domo_room", system_uuid)

        try:
            response = self._session_retry.get(
                complete_url, headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
        except RequestException as exc:
            raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc

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

                name = item.get("name")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError(f"apps[{i}].name is required and must not be empty")

                description = item.get("description")
                if description is not None and not isinstance(description, str):
                    raise ValueError(f"apps[{i}].description must be a string or null")
                data_controller_email = item.get("data_controller_email")
                if data_controller_email is not None and not isinstance(
                    data_controller_email, str
                ):
                    raise ValueError(
                        f"apps[{i}].data_controller_email must be a string or null"
                    )
                normalized_email = (
                    data_controller_email.strip()
                    if isinstance(data_controller_email, str)
                    else None
                )
                if normalized_email == "":
                    normalized_email = None

                applications.append(
                    SmartotumApplicationResult(
                        application_uuid = UUID(str(uuid.uuid4())),
                        name=str(name),
                        description=str(description),
                        data_controller_email=normalized_email,
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
            #there is also a field called id in value, for using it an idea is to edit the application table to show for every home the applications for that home
            #so the value.id can be unique in a home 
            description = None

            applications.append(
                SmartotumApplicationResult(
                    application_uuid=topic_uuid,
                    name=str(name),
                    description=description,
                    data_controller_email=None,
                )
            )

        return applications

    

    def login(self, email:str, password: str) -> SmartotumLoginResult:

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
