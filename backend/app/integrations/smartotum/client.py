from dataclasses import dataclass
from typing import Any, Dict, Optional
from ...exceptions import WrongUserCredentialsException
from requests import RequestException

import requests
from flask import current_app

@dataclass
class SmartotumLoginResult:
    user: Dict[str, Any]
    access_token: str
    refresh_token: str
    front_token: Optional[str]


class SmartotumClient:

    #initialize env variables
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        cfg = current_app.config
        self._base_url = cfg["SMARTOTUM_BASE_URL"].rstrip("/")
        self._api_base_path = cfg["SMARTOTUM_API_BASE_PATH"].strip("/")
        self._timeout = cfg.get("SMARTOTUM_TIMEOUT", 10)
        self._session = session or requests.Session()
        self._rid = cfg["SMARTOTUM_RID"]
        self._auth_mode = cfg["SMARTOTUM_AUTH_MODE"]

    #helper function that return the url to send api to
    def _url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"
    

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
                self._url(f"{self._api_base_path}/signin"),
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
    
    def get_systems(self, access_token: str) -> Dict[str, Any]:

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
                self._url("service/systems"), headers=headers, params=params, timeout=self._timeout
            )
            response.raise_for_status()
        except RequestException as exc:
            raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc
        
        return response.json()
    
    def get_home_devices(self, access_token: str, system_id: str) -> Dict[str, Any]:

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        try:
            response = self._session.get(
                self._url(f"/service/systems/{system_id}/devices"), headers=headers, timeout=self._timeout
            )
            response.raise_for_status()
        except RequestException as exc:
            raise WrongUserCredentialsException("Error occurred during Smartotum request") from exc
        
        return response.json()
