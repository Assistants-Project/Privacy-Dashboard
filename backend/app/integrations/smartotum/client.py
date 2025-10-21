from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from ...exceptions import WrongUserCredentialsException
from requests import RequestException
from uuid import UUID
import requests
from flask import current_app

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
class SmartotumDeviceResult:
    device_uuid: UUID
    name: str
    topic_name: str
    room_uuid: UUID | None = None #se non hanno una casa per il momento lasciamo none

class SmartotumClient:

    #initialize env variables
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        cfg = current_app.config
        self._base_url = cfg["SMARTOTUM_BASE_URL"].rstrip("/")
        self._base_dht_url = cfg["SMARTOTUM_DHT_URL"].rstrip("/")
        self._api_base_path = cfg["SMARTOTUM_API_BASE_PATH"].strip("/")
        self._smartotum_device_topics = cfg["SMARTOTUM_DEVICE_TOPICS"]
        self._timeout = cfg.get("SMARTOTUM_TIMEOUT", 10)
        self._session = session or requests.Session()
        self._rid = cfg["SMARTOTUM_RID"]
        self._auth_mode = cfg["SMARTOTUM_AUTH_MODE"]

    #helper function that return the url to send api to
    def smartotum_api_url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"
    
    def smartotum_dht_api_url(self, path: str, home_uuid: str) -> str:
        base = self._base_dht_url.replace("house_name", home_uuid)
        return f"{base}/{path.lstrip('/')}"


    def get_home_devices(self, access_token: str, system_uuid: str) -> List[SmartotumDeviceResult]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        devices: List[SmartotumDeviceResult] = []

        for topic_name in self._smartotum_device_topics:

            complete_url=self.smartotum_dht_api_url(f"/topic_name/{topic_name}", system_uuid)

            try:
                response = self._session.get(
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
            response = self._session.get(
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
            response = self._session.post(
                self.smartotum_api_url(f"{self._api_base_path}/signin"),
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except RequestException as exc:
            raise WrongUserCredentialsException("Error occurred during Smartotum login") from exc
    

        data = response.json()
        
        if data.get("status") == "WRONG_CREDENTIALS_ERROR" or "user" not in data:
            raise WrongUserCredentialsException("Invalid email or password!")
        
        access_token = response.headers.get("st-access-token")
        refresh_token = response.headers.get("st-refresh-token")

        if not access_token or not refresh_token:
            raise WrongUserCredentialsException("Smartotum login missing tokens")
        
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
            response = self._session.get(
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
