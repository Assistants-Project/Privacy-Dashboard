from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from requests import RequestException
from requests.exceptions import Timeout
from uuid import UUID
import requests
from flask import current_app
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import uuid


@dataclass
class MarketplaceApplicationResult:
    application_uuid: UUID
    name: str
    description: str | None = None



class MarketplaceClient:

    #initialize env variables
    def __init__(self) -> None:
        cfg = current_app.config
        self._applications_file = cfg.get("MARKETPLACE_APPLICATIONS_JSON")

    
    def update_marketplace_applications(self) -> List[MarketplaceApplicationResult]:

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
                raise ValueError("MARKETPLACE_APPLICATIONS_JSON must be an array")

            applications: List[MarketplaceApplicationResult] = []

            for i,item in enumerate(payload):
                    
                if not isinstance(item, dict):
                    raise ValueError(f"apps[{i}] must be an object")

                name = item.get("name")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError(f"apps[{i}].name is required and must not be empty")

                description = item.get("description")
                if description is not None and not isinstance(description, str):
                    raise ValueError(f"apps[{i}].description must be a string or null")

                applications.append(
                    MarketplaceApplicationResult(
                        application_uuid = UUID(str(uuid.uuid4())),
                        name=str(name),
                        description=str(description) if description is not None else None,
                    )
                )

            return applications
        
        applications: List[MarketplaceApplicationResult] = []

        #add here real marketplace when it's ready


        return applications
