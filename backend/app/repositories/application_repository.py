from datetime import datetime
from typing import Iterator, Tuple

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
