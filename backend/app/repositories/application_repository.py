from datetime import datetime
from typing import Iterator, Tuple
from uuid import UUID

from ..extensions import db
from ..models import Application, UserSmartHomeApplication


class ApplicationRepository:
    @staticmethod
    def get_applications_by_dc_or_dpo_id(
        user_id: int,
    ) -> Iterator[Tuple[Application, datetime]]:
        statement = db.select(Application, UserSmartHomeApplication.installed_at).join(
            Application.installed_by_user_smart_home_combinations.and_(
                UserSmartHomeApplication.user_id == user_id
            )
        )
        return db.session.execute(statement)

    @staticmethod
    def get_managed_application_by_uuid(
        user_id: int, application_uuid: UUID
    ) -> Application | None:
        statement = db.select(Application).join(
            Application.installed_by_user_smart_home_combinations.and_(
                UserSmartHomeApplication.user_id == user_id,
                Application.uuid == application_uuid,
            )
        )
        return db.session.scalar(statement)
