from flask import request
from ..exceptions import MissingJWTException, WrongUserCredentialsException
from ..integrations.smartotum import SmartotumClient

class SmartotumService:
    @staticmethod
    def get_homes() -> list[dict]:
        access_token = request.cookies.get("st_access_token")
        if not access_token:
            raise MissingJWTException("Smartotum access token missing")

        try:
            systems_data = SmartotumClient().get_systems(access_token)
        except WrongUserCredentialsException:
            # token not valid
            raise

        #for every home it returns only some information -> mapping between smartotum api response and our api
        return [
            {
                "uuid": item["id"],
                "name": item.get("name"),
                "address": item.get("address"),
                "zip_code": item.get("zip_code"),
                "country": item.get("country"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "timezone": item.get("timezone"),
                "language": item.get("language"),
            }
            for item in systems_data.get("data", []) #returns [] if the are no element
        ]