from typing import Iterator, Tuple

from ..extensions import db
from ..models import Application, Request, User, UserSmartHomeApplication


class RequestRepository:
    @staticmethod
    def get_requests_by_application_id_and_user_id(
        application_id: int,
        user_id: int,
    ) -> Iterator[Tuple[Request, str, str]]:
        statement = (
            db.select(
                Request,
                User.email,
                Application.name,
            )
            .join(
                Request.user_smart_home_application_relation.and_(
                    UserSmartHomeApplication.application_id == application_id,
                    UserSmartHomeApplication.user_id == user_id,
                )
            )
            .join(User)
            .join(Application)
        )
        return db.session.execute(statement)
