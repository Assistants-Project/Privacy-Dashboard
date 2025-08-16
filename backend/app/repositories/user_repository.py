from typing import List

from ..extensions import db
from ..models import User, UserRole, UserSmartHomeApplication


class UserRepository:
    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        statement = db.select(User).filter_by(email=email)
        return db.session.scalar(statement)

    @staticmethod
    def get_users_by_application_id_and_user_role(
        application_id: int, role: UserRole
    ) -> List[User]:
        statement = (
            db.select(User)
            .distinct()
            .join(
                User.installed_applications.and_(
                    UserSmartHomeApplication.application_id == application_id,
                    User.role == role,
                )
            )
        )
        return db.session.scalars(statement).all()
