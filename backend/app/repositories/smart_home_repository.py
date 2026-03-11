from ..extensions import db
from ..models import SmartHome, UserSmartHome


class SmartHomeRepository:
    @staticmethod
    def get_home_by_uuid(home_uuid: str) -> SmartHome | None:
        """Return the smart home with the given UUID, if present."""
        statement = db.select(SmartHome).where(SmartHome.uuid == home_uuid)
        return db.session.scalar(statement)

    @staticmethod
    def get_home_owners_by_home_id(home_id: int) -> list[int]:
        """Return the id of the user owners of the smart home"""
        statement = db.select(UserSmartHome.user_id).where(
            UserSmartHome.smart_home_id == home_id
        )
        return list(db.session.scalars(statement))

    @staticmethod
    def get_homes_by_user_id(user_id: int) -> list[SmartHome]:
        """Return the smart homes of a given user, if present."""
        # to check
        statement = (
            db.select(SmartHome)
            .join(UserSmartHome, UserSmartHome.smart_home_id == SmartHome.id)
            .where(UserSmartHome.user_id == user_id)
        )
        return list(db.session.scalars(statement))

    @staticmethod
    def assign_home(home_id: int, user_id: int):
        """Assign a user to a smart home"""
        statement = (
            db.select(UserSmartHome)
            .where(UserSmartHome.smart_home_id == home_id)
            .where(UserSmartHome.user_id == user_id)
        )
        relation = db.session.scalar(statement)

        if relation is None:
            relation = UserSmartHome()
            relation.smart_home_id = home_id
            relation.user_id = user_id
            db.session.add(relation)

        return relation
    
    @staticmethod
    def unassign_home(home_id: int, user_id: int) -> None:
        """Remove the ownership relation between a user and a smart home, if present."""
        statement = (
            db.select(UserSmartHome)
            .where(UserSmartHome.smart_home_id == home_id)
            .where(UserSmartHome.user_id == user_id)
        )
        relation = db.session.scalar(statement)
        if relation is not None:
            db.session.delete(relation)

    @staticmethod
    def delete_home(home: SmartHome) -> None:
        db.session.delete(home)

    @staticmethod
    def upsert_home(
        home_uuid: str,
        name: str,
        address: str,
        zip_code: str | None = None,
        country: str | None = None,
    ) -> SmartHome:
        """Create or update a SmartHome given the UUID."""
        home = SmartHomeRepository.get_home_by_uuid(home_uuid)

        if home is None:
            home = SmartHome(
                uuid=home_uuid,
                name=name,
                address=address or "",
                zip_code=zip_code or None,
                country=country or None,
            )
            db.session.add(home)
            db.session.flush()
            return home

        home.name = name
        home.address = address or ""
        home.zip_code = zip_code or None
        home.country = country or None
        return home

    @staticmethod
    def get_home_by_ds_id_and_home_uuid(
        user_id: int, home_uuid: str
    ) -> SmartHome | None:
        statement = db.select(SmartHome).join(
            SmartHome.owned_by_users.and_(
                UserSmartHome.user_id == user_id,
                SmartHome.uuid == home_uuid,
            )
        )
        return db.session.scalar(statement)
