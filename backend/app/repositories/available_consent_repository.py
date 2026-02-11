from datetime import datetime
from typing import Iterator, Tuple
from uuid import UUID

from sqlalchemy import Row

from ..extensions import db
from ..models import Application, AvailableConsent, UserSmartHomeAvailableConsent


class AvailableConsentRepository:
    #si occupa di aggiungere consensi mancanti, se un consenso è già presente non fa nulla
    #utilizzata sia nel contesto di sync smartotum sia nel caso di creazione di una nuova app
    #non cancella i consensi non più presenti -> bisogna decidere come gestire la cancellazione -> avere is active = false sarebbe la soluzione migliore
    @staticmethod
    def upsert_available_consents_for_application(application_id: int, available_consent_contents: list[str]) -> None:

        if not available_consent_contents:
            return

        statement = db.select(AvailableConsent.content).where(AvailableConsent.application_id == application_id)
        existing_contents = set(db.session.scalars(statement).all())

        for content in available_consent_contents:
            if content in existing_contents:
                continue
            db.session.add(AvailableConsent(content=content, application_id=application_id))
            existing_contents.add(content)
        return

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
    def get_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_application_id(
        user_id: int, smart_home_id: int, application_id: int
    ) -> Row | None:
        statement = db.select(UserSmartHomeAvailableConsent).join(
            UserSmartHomeAvailableConsent.available_consent.and_(
                UserSmartHomeAvailableConsent.user_id == user_id,
                UserSmartHomeAvailableConsent.smart_home_id == smart_home_id,
                AvailableConsent.application_id == application_id,
            )
        )
        return db.session.execute(statement).first()

    @staticmethod
    def get_available_consents_by_ds_id_and_smart_home_id(
        current_user_id: int, smart_home_id: int
    ) -> Iterator[Tuple[AvailableConsent, UUID, datetime]]:
        statement = (
            db.select(
                AvailableConsent,
                Application.uuid,
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

    @staticmethod
    def delete_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_available_consent_id(
        user_id: int, smart_home_id: int, available_consent_id: int
    ) -> None:
        statement = db.delete(UserSmartHomeAvailableConsent).where(
            UserSmartHomeAvailableConsent.user_id == user_id,
            UserSmartHomeAvailableConsent.smart_home_id == smart_home_id,
            UserSmartHomeAvailableConsent.available_consent_id == available_consent_id,
        )
        db.session.execute(statement)
        db.session.commit()
        return

    @staticmethod
    def delete_user_smart_home_available_consent_by_ds_id_and_smart_home_id_and_application_id(
        user_id: int, smart_home_id: int, application_id: int
    ) -> None:
        subquery = (
            db.select(AvailableConsent.id)
            .where(AvailableConsent.application_id == application_id)
            .subquery()
        )
        statement = db.delete(UserSmartHomeAvailableConsent).where(
            UserSmartHomeAvailableConsent.user_id == user_id,
            UserSmartHomeAvailableConsent.smart_home_id == smart_home_id,
            UserSmartHomeAvailableConsent.available_consent_id.in_(subquery),
        )
        db.session.execute(statement)
        db.session.commit()
        return
    
    #no commit at the end so the update_database_smartotum can do it at the end if the process is succefull
    @staticmethod
    def delete_user_smart_home_available_consents_by_ds_id_and_smart_home_id(
        user_id: int, smart_home_id: int
    ) -> None:
        statement = db.delete(UserSmartHomeAvailableConsent).where(
            UserSmartHomeAvailableConsent.user_id == user_id,
            UserSmartHomeAvailableConsent.smart_home_id == smart_home_id,
        )
        db.session.execute(statement)
        return
    #revoca specifici consensi da una casa di un utente per una specifica app -> id del consenso è già legato ad 
    #un consenso specifico per una determinata app
    @staticmethod
    def delete_user_smart_home_available_consents_by_ds_id_and_smart_home_id_and_available_consent_ids(
        user_id: int, smart_home_id: int, available_consent_ids: list[int]
    ) -> None:
        if not available_consent_ids:
            return
        statement = db.delete(UserSmartHomeAvailableConsent).where(
            UserSmartHomeAvailableConsent.user_id == user_id,
            UserSmartHomeAvailableConsent.smart_home_id == smart_home_id,
            UserSmartHomeAvailableConsent.available_consent_id.in_(available_consent_ids),
        )
        db.session.execute(statement)
        return
