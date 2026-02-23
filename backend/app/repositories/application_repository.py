from datetime import datetime
from typing import Iterator, List, Tuple
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import aliased

from ..extensions import db
from ..models import Application, Evaluation, User, UserRole, UserSmartHomeApplication


class ApplicationRepository:
    @staticmethod
    def get_application_by_uuid(application_uuid: UUID) -> Application | None:
        statement = db.select(Application).where(Application.uuid == application_uuid)
        return db.session.scalar(statement)

    @staticmethod
    def get_application_by_name(application_name: str) -> Application | None:
        statement = db.select(Application).where(Application.name == application_name)
        return db.session.scalar(statement)

    @staticmethod
    def create_application(
        name: str,
        description: str | None,
        title: str,
        owner_user_id: int | None = None,
    ) -> Application:
        application = Application(
            name=name,
            title=title,
            description=description,
            owner_user_id=owner_user_id,
        )
        db.session.add(application)
        db.session.flush()
        return application

    @staticmethod
    def get_applications_by_dc_or_dpo_id(
        user_id: int,
    ) -> List[Tuple[Application, datetime, User | None]]:
        current_user_rel = aliased(UserSmartHomeApplication)
        manager_rel = aliased(UserSmartHomeApplication)

        statement = (
            db.select(Application, current_user_rel.installed_at, User)
            .join(
                current_user_rel,
                and_(
                    current_user_rel.application_id == Application.id,
                    current_user_rel.user_id == user_id,
                    current_user_rel.smart_home_id.is_(None),
                ),
            )
            .outerjoin(
                manager_rel,
                and_(
                    manager_rel.application_id == Application.id,
                    manager_rel.smart_home_id.is_(None),
                ),
            )
            .outerjoin(
                User,
                and_(
                    User.id == manager_rel.user_id,
                    User.role.in_(
                        [
                            UserRole.DATA_CONTROLLER,
                            UserRole.DATA_PROTECTION_OFFICER,
                        ]
                    ),
                ),
            )
        )
        rows = db.session.execute(statement).all()
        return [(app, installed_at, user) for app, installed_at, user in rows]

    @staticmethod
    def get_application_by_user_id_and_application_uuid(
        user_id: int, application_uuid: UUID
    ) -> Application | None:
        statement = db.select(Application).join(
            Application.installed_by_user_smart_home_combinations.and_(
                UserSmartHomeApplication.user_id == user_id,
                Application.uuid == application_uuid,
            )
        )
        return db.session.scalar(statement)

    @staticmethod
    def get_installed_application_by_ds_id_and_application_uuid(
        user_id: int, application_uuid: UUID
    ) -> Application | None:
        statement = db.select(Application).join(
            Application.installed_by_user_smart_home_combinations.and_(
                UserSmartHomeApplication.user_id == user_id,
                UserSmartHomeApplication.smart_home_id.isnot(None),
                Application.uuid == application_uuid,
            )
        )
        return db.session.scalar(statement)

    @staticmethod
    def get_applications_by_ds_id_and_smart_home_id(
        user_id: int, smart_home_id: int
    ) -> Iterator[Tuple[Application, datetime]]:
        statement = db.select(Application, UserSmartHomeApplication.installed_at).join(
            Application.installed_by_user_smart_home_combinations.and_(
                UserSmartHomeApplication.user_id == user_id,
                UserSmartHomeApplication.smart_home_id == smart_home_id,
            )
        )
        return db.session.execute(statement)

    @staticmethod
    def get_installed_applications_with_managers_by_ds_id_and_smart_home_id(
        user_id: int, smart_home_id: int
    ) -> List[Tuple[Application, datetime, User | None]]:
        ds_rel = aliased(UserSmartHomeApplication)
        mgr_rel = aliased(UserSmartHomeApplication)

        statement = (
            db.select(Application, ds_rel.installed_at, User)
            .join(
                ds_rel,
                and_(
                    ds_rel.application_id == Application.id,
                    ds_rel.user_id == user_id,
                    ds_rel.smart_home_id == smart_home_id,
                ),
            )
            .outerjoin(
                mgr_rel,
                and_(
                    mgr_rel.application_id == Application.id,
                    mgr_rel.smart_home_id.is_(None),
                ),
            )
            .outerjoin(
                User,
                and_(
                    User.id == mgr_rel.user_id,
                    User.role.in_(
                        [
                            UserRole.DATA_CONTROLLER,
                            UserRole.DATA_PROTECTION_OFFICER,
                        ]
                    ),
                ),
            )
        )

        rows = db.session.execute(statement).all()
        return [(app, installed_at, user) for app, installed_at, user in rows]

    @staticmethod
    def get_user_smart_home_application_by_ds_id_and_smart_home_id_and_application_uuid(
        user_id: int, smart_home_id: int, application_uuid: UUID
    ) -> UserSmartHomeApplication | None:
        statement = db.select(UserSmartHomeApplication).join(
            UserSmartHomeApplication.application.and_(
                UserSmartHomeApplication.user_id == user_id,
                UserSmartHomeApplication.smart_home_id == smart_home_id,
                Application.uuid == application_uuid,
            )
        )
        return db.session.scalar(statement)

    @staticmethod
    def get_user_smart_home_application_by_ds_id_and_smart_home_id_and_application_id(
        user_id: int, smart_home_id: int, application_id: int
    ) -> UserSmartHomeApplication | None:
        statement = db.select(UserSmartHomeApplication).where(
            UserSmartHomeApplication.user_id == user_id,
            UserSmartHomeApplication.smart_home_id == smart_home_id,
            UserSmartHomeApplication.application_id == application_id,
        )
        return db.session.scalar(statement)

    @staticmethod
    def update_application_evaluation(
        application_id: int, evaluation: Evaluation, questionnaire_summary: str
    ) -> None:
        application = db.session.get(Application, application_id)
        application.evaluation = evaluation
        application.questionnaire_summary = questionnaire_summary
        db.session.commit()

    @staticmethod
    def update_applications_for_home(
        user_id: int, smart_home_id: int, applications: List[Application]
    ) -> None:
        """Upserts applications by name and syncs user-home installed applications relations."""

        applications_by_name: dict[str, Application] = {}
        for application in applications:
            name = (application.name or "").strip()
            if not name:
                continue
            application.name = name
            applications_by_name[name] = application

        input_names = set(applications_by_name.keys())
        existing_by_name: dict[str, Application] = {}
        if input_names:
            statement = db.select(Application).where(Application.name.in_(input_names))
            existing_by_name = {
                application.name: application
                for application in db.session.scalars(statement).all()
            }

        desired_application_ids: set[int] = set()

        for name, application in applications_by_name.items():
            present = existing_by_name.get(name)
            if present is None:
                db.session.add(application)
                db.session.flush()
                present = application
                existing_by_name[name] = present
            else:
                if application.title is not None:
                    present.title = application.title
                if application.description is not None:
                    present.description = application.description

            desired_application_ids.add(present.id)

        rel_statement = db.select(UserSmartHomeApplication).where(
            UserSmartHomeApplication.user_id == user_id,
            UserSmartHomeApplication.smart_home_id == smart_home_id,
        )
        relations_present = list(db.session.scalars(rel_statement).all())
        relations_by_app_id = {rel.application_id: rel for rel in relations_present}

        for application_id in desired_application_ids:
            if application_id in relations_by_app_id:
                continue
            relation = UserSmartHomeApplication()
            relation.user_id = user_id
            relation.smart_home_id = smart_home_id
            relation.application_id = application_id
            relation.installed_at = datetime.now()
            db.session.add(relation)

        for rel in relations_present:
            if rel.application_id not in desired_application_ids:
                db.session.delete(rel)

    @staticmethod
    def ensure_application_managed_by_user(user_id: int, application_id: int) -> bool:
        # Assicura che l'utente sia collegato all'app come "manager" (Data Controller / DPO)
        # Nel nostro modello, un'app "managed" è una riga in UserSmartHomeApplication con smart_home_id = NULL
        # La funzione è idempotente:
        # - se la relazione esiste già, non crea nulla e ritorna False
        # - se non esiste, la crea e ritorna True
        # In più elimina eventuali duplicati: con il vincolo UNIQUE attuale i NULL possono permettere righe doppie

        statement = db.select(UserSmartHomeApplication).where(
            UserSmartHomeApplication.user_id == user_id,
            UserSmartHomeApplication.smart_home_id.is_(None),
            UserSmartHomeApplication.application_id == application_id,
        )
        relations = list(db.session.scalars(statement).all())
        if relations:
            # Se ci sono più righe (duplicati), teniamo la prima e cancelliamo le altre.
            for duplicate in relations[1:]:
                db.session.delete(duplicate)
            return False

        # Relazione non presente: la creiamo (user_id + application_id) come "managed" (smart_home_id = NULL)
        relation = UserSmartHomeApplication()
        relation.user_id = user_id
        relation.smart_home_id = None
        relation.application_id = application_id
        relation.installed_at = datetime.now()
        db.session.add(relation)
        return True

    @staticmethod
    def remove_application_managed_by_user(user_id: int, application_id: int) -> bool:
        statement = db.select(UserSmartHomeApplication).where(
            UserSmartHomeApplication.user_id == user_id,
            UserSmartHomeApplication.smart_home_id.is_(None),
            UserSmartHomeApplication.application_id == application_id,
        )
        relations = list(db.session.scalars(statement).all())
        if not relations:
            return False

        for relation in relations:
            db.session.delete(relation)
        return True

    @staticmethod
    def replace_data_controller_for_application( application_id: int, data_controller_user_id: int) -> bool:
        """Ensures that the given Data Controller is the only DC manager of the application.

        Returns:
            True if a new relation is created or an old DC relation is replaced.
            False if the selected Data Controller was already the only assigned one.
        """

        statement = (
            db.select(UserSmartHomeApplication)
            .join(User, User.id == UserSmartHomeApplication.user_id)
            .where(
                UserSmartHomeApplication.application_id == application_id,
                UserSmartHomeApplication.smart_home_id.is_(None),
                User.role == UserRole.DATA_CONTROLLER,
            )
        )
        relations = list(db.session.scalars(statement).all())

        kept = None
        changed = False
        for relation in relations:
            if relation.user_id == data_controller_user_id and kept is None:
                kept = relation
                continue
            db.session.delete(relation)
            changed = True

        if kept is not None:
            return changed

        relation = UserSmartHomeApplication()
        relation.user_id = data_controller_user_id
        relation.smart_home_id = None
        relation.application_id = application_id
        relation.installed_at = datetime.now()
        db.session.add(relation)
        return True

    @staticmethod
    def has_dpo_assigned_for_application(application_id: int) -> bool:
        statement = (
            db.select(UserSmartHomeApplication.id)
            .join(User, User.id == UserSmartHomeApplication.user_id)
            .where(
                UserSmartHomeApplication.application_id == application_id,
                UserSmartHomeApplication.smart_home_id.is_(None),
                User.role == UserRole.DATA_PROTECTION_OFFICER,
            )
        )
        return db.session.scalar(statement) is not None

    @staticmethod
    def get_dpo_user_ids_for_application(application_id: int) -> set[int]:
        # Restituisce gli id degli utenti DPO assegnati ad una specifica app
        # join con User per filtrare solo i DPO, e smart_home_id = NULL
        statement = (
            db.select(UserSmartHomeApplication.user_id)
            .join(User, User.id == UserSmartHomeApplication.user_id)
            .where(
                UserSmartHomeApplication.application_id == application_id,
                UserSmartHomeApplication.smart_home_id.is_(None),
                User.role == UserRole.DATA_PROTECTION_OFFICER,
            )
        )
        return set(db.session.scalars(statement).all())

    @staticmethod
    def get_data_controller_user_ids_for_application(application_id: int) -> set[int]:
        statement = (
            db.select(UserSmartHomeApplication.user_id)
            .join(User, User.id == UserSmartHomeApplication.user_id)
            .where(
                UserSmartHomeApplication.application_id == application_id,
                UserSmartHomeApplication.smart_home_id.is_(None),
                User.role == UserRole.DATA_CONTROLLER,
            )
        )
        return set(db.session.scalars(statement).all())

    @staticmethod
    def assign_dpo_for_application(application_id: int, dpo_user_id: int) -> None:
        # Assegna un DPO ad una app come relazione "managed" (smart_home_id = NULL).
        # Obiettivo: avere un solo DPO collegato a questa app.
        # - se il DPO è già presente, non facciamo nulla (a parte cancellare eventuali duplicati)
        # - se esistono altri DPO assegnati, li rimuoviamo
        # - se non esiste nessun DPO, creiamo la relazione per dpo_user_id

        statement = (
            db.select(UserSmartHomeApplication)
            .join(User, User.id == UserSmartHomeApplication.user_id)
            .where(
                UserSmartHomeApplication.application_id == application_id,
                UserSmartHomeApplication.smart_home_id.is_(None),
                User.role == UserRole.DATA_PROTECTION_OFFICER,
            )
        )
        relations = list(db.session.scalars(statement).all())

        kept = None
        for relation in relations:
            if relation.user_id == dpo_user_id and kept is None:
                kept = relation
                continue
            # Se è un altro DPO (o un duplicato), lo cancelliamo.
            db.session.delete(relation)

        if kept is not None:
            # Il DPO richiesto era già assegnato (abbiamo solo ripulito eventuali duplicati)
            return

        # Nessun DPO assegnato: creiamo la relazione
        relation = UserSmartHomeApplication()
        relation.user_id = dpo_user_id
        relation.smart_home_id = None
        relation.application_id = application_id
        relation.installed_at = datetime.now()
        db.session.add(relation)

    @staticmethod
    def upsert_applications(applications: List[Application]) -> None:
        """Upserts applications by name only (no relations).
        Called only from marketplace"""

        applications_by_name: dict[str, Application] = {}
        for application in applications:
            name = (application.name or "").strip()
            if not name:
                continue
            application.name = name
            applications_by_name[name] = application

        input_names = set(applications_by_name.keys())
        existing_by_name: dict[str, Application] = {}
        if input_names:
            statement = db.select(Application).where(Application.name.in_(input_names))
            existing_by_name = {
                application.name: application
                for application in db.session.scalars(statement).all()
            }

        for name, application in applications_by_name.items():
            present = existing_by_name.get(name)
            if present is None:
                db.session.add(application)
                db.session.flush()
                continue

            if application.title is not None:
                present.title = application.title
            if application.description is not None:
                present.description = application.description
