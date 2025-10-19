from typing import Iterator, List
from uuid import UUID

from ..extensions import db
from ..models import User, UserRole, UserSmartHomeApplication
from typing import Iterable


class UserRepository:

    @staticmethod
    def register_user(email: str, role: UserRole, firstname: str, lastname: str, password_hash: str | None = None, user_uuid: UUID | None = None) -> User | None:
        
        user = User( 
            email=email,
            firstname=firstname,
            lastname=lastname,
            role=role,
            password_hash=password_hash or ""
        )

        if user_uuid is not None:
            user.uuid = user_uuid #for smartotum data subject

        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        statement = db.select(User).where(User.email == email)
        return db.session.scalar(statement)

    @staticmethod
    def get_user_by_uuid(uuid: UUID) -> User | None:
        statement = db.select(User).where(User.uuid == uuid)
        return db.session.scalar(statement)

    @staticmethod
    def get_users_by_application_id_and_user_role(
        application_id: int, role: UserRole
    ) -> Iterator[User]:
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
        return db.session.scalars(statement)

    @staticmethod
    def get_contacts_by_dc_or_dpo_id(user_id: int) -> Iterable[User]:
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

    @staticmethod
    def get_contact_by_dc_or_dpo_id_and_other_user_uuid(
        user_id: int, other_user_uuid: UUID
    ) -> User | None:
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
                    User.uuid == other_user_uuid,
                    UserSmartHomeApplication.user_id != user_id,
                    UserSmartHomeApplication.application_id.in_(db.select(subquery)),
                )
            )
        )
        return db.session.scalar(statement)
