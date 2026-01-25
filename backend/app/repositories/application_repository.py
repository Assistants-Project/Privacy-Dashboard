from datetime import datetime
from typing import Iterator, List, Tuple
from uuid import UUID

from ..extensions import db
from ..models import Application, Evaluation, UserSmartHomeApplication, User, UserRole
from sqlalchemy import and_
from sqlalchemy.orm import aliased



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
        application_id: int, evaluation: Evaluation
    ) -> None:
        application = db.session.get(Application, application_id)
        application.evaluation = evaluation
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
    def submit_pia_for_application(application_id: int, pia_data: dict) -> None:
        application = db.session.get(Application, application_id)
        application.privacy_impact_assessment = pia_data
        db.session.commit()

    #retrieves for every application the applications details and assigned data controllers and dpo
    @staticmethod
    def get_available_application() -> List[Tuple[Application, User | None]]:

        statement = (db.select(Application, User).outerjoin(
            UserSmartHomeApplication,
            and_(
                UserSmartHomeApplication.application_id == Application.id,
                UserSmartHomeApplication.smart_home_id.is_(None),
            ),
        )
        .outerjoin(User,and_(
        User.id == UserSmartHomeApplication.user_id,
        User.role.in_([UserRole.DATA_CONTROLLER, UserRole.DATA_PROTECTION_OFFICER]),
        )))

        rows = db.session.execute(statement).all()

        return [(app, user) for app, user in rows]
