from typing import List

from ..extensions import db
from ..models import User, UserRole, UserSmartHomeApplication


class UserRepository:
    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        statement = db.select(User).where(User.email == email)
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

    @staticmethod
    def get_contacts_by_dc_or_dpo_id(user_id: int) -> List[User]:
        subquery = (
            db.select(UserSmartHomeApplication.application_id)
            .where(UserSmartHomeApplication.user_id == user_id)
            .subquery()
        )
        statement = (
            db.select(User)
            .distinct()
            .join(
                User.installed_applications.and_(
                    UserSmartHomeApplication.user_id != user_id,
                    UserSmartHomeApplication.application_id.in_(db.select(subquery)),
                )
            )
        )
        return db.session.scalars(statement).all()
