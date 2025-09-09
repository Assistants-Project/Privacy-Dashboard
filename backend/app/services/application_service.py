from datetime import datetime
from typing import List, TypedDict

from ..models import Application
from ..repositories import ApplicationRepository


class ApplicationDict(TypedDict):
    application: Application
    installed_at: datetime


class ApplicationService:
    @staticmethod
    def get_applications_by_dc_or_dpo_id(
        user_id: int,
    ) -> List[ApplicationDict]:
        """Returns a list of applications fetched by a `DATA_CONTROLLER` or `DPO`'s id from the database,
        along with the date and time they were installed.

        Args:
            user_id: The ID of the user with role `DATA_CONTROLLER` or `DPO` who manages the applications.

        Returns:
            A list of dictionaries each containing the application instance and the date and time it was installed
            by the given user, or an empty list if none are found.
        """

        iterator = ApplicationRepository.get_applications_by_dc_or_dpo_id(user_id)
        return [{"application": app, "installed_at": dt} for app, dt in iterator]
