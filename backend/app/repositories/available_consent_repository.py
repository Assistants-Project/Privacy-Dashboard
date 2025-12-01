from datetime import datetime
from typing import Iterator, Tuple
from uuid import UUID

from sqlalchemy import Row

from ..extensions import db
from ..models import Application, AvailableConsent, UserSmartHomeAvailableConsent


class AvailableConsentRepository:
    @staticmethod
    def get_available_consent_by_uuid(consent_uuid: UUID) -> Row | None:
        statement = db.select(
            AvailableConsent.id, AvailableConsent.application_id
        ).where(AvailableConsent.uuid == consent_uuid)
        return db.session.execute(statement).first()

    @staticmethod
    def get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
        user_id: int, smart_home_id: int, available_consent_id: int
    ) -> UserSmartHomeAvailableConsent | None:
        statement = db.select(UserSmartHomeAvailableConsent).where(
            UserSmartHomeAvailableConsent.user_id == user_id,
            UserSmartHomeAvailableConsent.smart_home_id == smart_home_id,
            UserSmartHomeAvailableConsent.available_consent_id == available_consent_id,
        )
        return db.session.scalar(statement)

    @staticmethod
    def get_available_consents_by_ds_id_and_smart_home_id(
        current_user_id: int, smart_home_id: int
    ) -> Iterator[Tuple[AvailableConsent, str, datetime]]:
        statement = (
            db.select(
                AvailableConsent,
                Application.name,
                UserSmartHomeAvailableConsent.given_at,
            )
            .join(
                AvailableConsent.given_by_user_smart_home_combinations.and_(
                    UserSmartHomeAvailableConsent.smart_home_id == smart_home_id,
                    UserSmartHomeAvailableConsent.user_id == current_user_id,
                )
            )
            .join(Application)
        )
        return db.session.execute(statement)

    @staticmethod
    def create_user_smart_home_available_consent(
        user_id: int,
        smart_home_id: int,
        available_consent_id: int,
    ) -> UserSmartHomeAvailableConsent:
        given_consent = UserSmartHomeAvailableConsent(
            user_id=user_id,
            smart_home_id=smart_home_id,
            available_consent_id=available_consent_id,
            given_at=datetime.now(),
        )
        db.session.add(given_consent)
        db.session.commit()
        db.session.refresh(given_consent)
        return given_consent
